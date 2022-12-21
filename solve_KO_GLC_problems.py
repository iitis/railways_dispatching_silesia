import pickle as pkl
import time
import pulp as pl


from data_formatting.data_formatting import (
    add_delay,
    get_skip_stations
)
from railway_solvers.railway_solvers import (
    annealing,
    convert_to_bqm,
    create_linear_problem,
    get_results,
    get_best_feasible_sample,
    convert_to_cqm,
    constrained_solver,
    count_quadratic_couplings,
    count_linear_fields

)

from helpers import (
    load_important_stations,
    build_timetables,
    load_data_paths,
    make_taus,
    make_timetable,
    make_train_set,
    print_optimisation_results,
    check_count_vars,
    count_vars
)




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Make variables to problem from dataframes, parameters of problem and solutions")
    

    parser.add_argument(
        "--case",
        type=int,
        help="Case of railway problem",
        default=1,
    )

    parser.add_argument(
        "--category",
        type=str,
        help="category of time variables integer in contionious",
        default="Integer",
    )

    parser.add_argument(
        "--solve_lp",
        type=str,
        help="LP solver of PuLp librery e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'",
        default="",
    )

    parser.add_argument(
        "--solve_quantum",
        type=str,
        help="quantum or quantum inspired solver: 'sim' - D-Wave simulation, 'real' - D-Wave, 'hyb' - D-Wave hybrid via QUBO,  'cqm' - D-Wave hybrid cqm, 'save_qubo' just save qubo to ./qubos",
        default="",
    )

    args = parser.parse_args()

    # paths to files
    if args.case == 1:
        important_stations_path = "./data/KO_GLC/important_stations_KO_GLC.npz"
        data_paths = load_data_paths("./data/network_paths.ods")
        d = "./data/KO_GLC/trains_schedules_KO_GLC.csv"

    important_stations = load_important_stations(important_stations_path)
    train_dict = build_timetables(d, False, important_stations, data_paths)
    taus = make_taus(train_dict, important_stations, r=0)  # r = 0 no rounding
    skip_stations = get_skip_stations(train_dict)
    train_set = make_train_set(
        train_dict, important_stations, data_paths, skip_stations
    )
    t_ref = "14:00"

    assert args.solve_quantum in ["", "sim", "real", "hyb", "cqm"]
    

    # input

    d_max = 40

    disturbances = {}
    disturbances[0] = dict()
    disturbances[1] = dict({4601:3})
    disturbances[2] = dict({4601:3, 4603:5})
    #disturbances[3] = dict({1:2, 3:2, 5:7})
    #disturbances[4] = dict({2:2, 4:2, 4605:3, 4607:3})
    #disturbances[5] = dict({1:5, 2:3, 3:7, 4:2, 5:1, 4601:2})
    #disturbances[6] = dict({3:7, 4:2, 5:1, 23: 6, 31:6, 4611:2, 101: 4, 6402: 7})
    #disturbances[7] = dict({1: 5, 11: 3, 21:3, 31:2, 2:4, 4:2, 6:6, 8:3, 10:3, 22: 6, 24:7, 40: 6, 36: 1})
    #disturbances[8] = dict({1:3, 2:5, 3:7, 4:27, 5:8, 6:12, 7:17, 23: 4, 25: 6, 25: 8, 27: 11, 31:3, 32: 8, 10:4, 6401:3, 6403: 7, 101:8})
    #disturbances[9] = dict({2: 3, 4602:1, 4: 10, 102: 2, 6: 15, 8: 7, 4604: 4, 10: 1, 12: 7, 1: 10, 101: 8, 3: 2, 6401: 6, 5: 15, 7: 1, 103: 30, 9: 7, 6403: 8})
    #disturbances[10] = dict({i: i%3 for i in train_set["J"]})
    #disturbances[11] = dict({i: i%10 for i in train_set["J"]})


    pdict = {
        "minimal_span": 2.5,
        "single_line": 2.5,
        "minimal_stay": 2.5,
        "track_occupation": 2.5,
        "switch": 2.5,
        "occupation": 2.5,
        "circulation": 2.5,
        "objective": 1,
    }

    sim_annealing_var = {"beta_range": (0.001, 10), "num_sweeps": 10, "num_reads": 2}
    real_anneal_var_dict = {"num_reads": 3996, "annealing_time": 250, "chain_strength": 4}


    results = {}
    results["method"] = args.solve_lp
    results["d_max"] = d_max
    results["case"] = args.case


    for k in disturbances:
        dist = disturbances[k]

        timetable = make_timetable(train_dict, important_stations, skip_stations, t_ref)
        for i in dist:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], i, dist[i]
            )

        result = {}  
        prob = create_linear_problem(train_set, timetable, d_max, cat=args.category)

        order_vars, int_vars, constraints = count_vars(prob)   
        result["order_vars"] = order_vars
        result["int_vars"] = int_vars
        result["constraints"] = constraints


        if args.solve_lp != "":
            if "CPLEX_CMD" == args.solve_lp:
                print("cplex")
                path_to_cplex = r'/home/ludmila/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex'
                solver =  pl.CPLEX_CMD(path=path_to_cplex)
            else:    
                solver = pl.getSolver(args.solve_lp)

            start_time = time.time()
            prob.solve(solver = solver)
            end_time = time.time()
            visualize = False
            if visualize:
                print_optimisation_results(prob, timetable, train_set, skip_stations, d_max, t_ref)

            result["objective"] = prob.objective.value() * d_max
            result["comp_time_seconds"] = end_time - start_time
            result["feasible"] = True
            results["brolen_constraints"] = 0


            check_count_vars(prob)

        elif args.solve_quantum in ["sim", "real", "hyb"]:
            bqm, qubo, interpreter = convert_to_bqm(prob, pdict)
            
            print(f"{args.solve_quantum} annealing")
            start_time = time.time()
            sampleset = annealing(bqm, interpreter, args.solve_quantum, sim_anneal_var_dict=sim_annealing_var, real_anneal_var_dict=real_anneal_var_dict)
            
            result["comp_time_seconds"] = time.time() - start_time
            dict_list = get_results(sampleset, prob=prob)
            sample = get_best_feasible_sample(dict_list)
            result.update(sample)
            results["broken_constraints"] = constraints - len(sample["feas_constraints"])

        elif args.solve_quantum == "cqm":
            cqm, interpreter = convert_to_cqm(prob)
            start_time = time.time()
            sampleset = constrained_solver(cqm)
            
            result["comp_time_seconds"] = time.time() - start_time
            dict_list = get_results(sampleset, prob=prob)
            sample = get_best_feasible_sample(dict_list)
            result.update(sample)
            results["broken_constraints"] = constraints - len(sample["feas_constraints"])
        
        results[k] = result
    
    results["samples"] = k+1

    file = f"results_KO_GLC/results_{args.solve_lp}_{args.solve_quantum}_{args.case}_{args.category}.pkl"
    with open(file, "wb") as f:
        pkl.dump(results, f)
    

