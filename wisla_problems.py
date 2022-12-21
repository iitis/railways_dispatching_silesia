import pickle as pkl
import time
import pulp as pl


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


from helpers import(
    print_optimisation_results,
    check_count_vars
    )



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Solutions methods")

    d_max = 10


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

    

    train_set = {
        "skip_station": {
            "Ks1": 10, "Ks3": 10, "Ic1": 10, "Ks2": 1, "Ks4":1, "Ic2":1},
        "Paths": { "Ks1": [1,3,5,10], "Ks3": [1,3,5,10], "Ic1": [1,3,5,10], "Ks2": [10,5,3,1], "Ks4": [10,5,3,1], "Ic2": [10,5,3,1]},
        "J": ["Ks1", "Ks3", "Ic1", "Ks2", "Ks4", "Ic2"],
        "Jd": {1: {3: [["Ks1", "Ks3", "Ic1"]]}, 3:{1:[["Ks2", "Ks4", "Ic2"]], 5:[["Ks1", "Ks3", "Ic1"]]}, 
               5:{3:[["Ks2", "Ks4", "Ic2"]], 10:[["Ks1", "Ks3", "Ic1"]]}}, 10:{5:[["Ks2", "Ks4", "Ic2"]]},
        "Josingle": {(1,3): [["Ks1", "Ks2"], ["Ks1", "Ks4"], ["Ks1", "Ic2"], ["Ks3", "Ks2"], ["Ks3", "Ks4"], ["Ks3", "Ic2"], ["Ic1", "Ks2"], ["Ic1", "Ks4"], ["Ic1", "Ic2"]],
                    (3,5): [["Ks1", "Ks2"], ["Ks1", "Ks4"], ["Ks1", "Ic2"], ["Ks3", "Ks2"], ["Ks3", "Ks4"], ["Ks3", "Ic2"], ["Ic1", "Ks2"], ["Ic1", "Ks4"], ["Ic1", "Ic2"]],
                    (5,10): [["Ks1", "Ks2"], ["Ks1", "Ks4"], ["Ks1", "Ic2"], ["Ks3", "Ks2"], ["Ks3", "Ks4"], ["Ks3", "Ic2"], ["Ic1", "Ks2"], ["Ic1", "Ks4"], ["Ic1", "Ic2"]]
                    },
        "Jround": {10: [["Ic1", "Ic2"]]},
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    taus = {"pass": {"Ks1_1_3": 4, "Ks1_3_5": 6, "Ks1_5_10": 6, "Ks3_1_3": 4, "Ks3_3_5": 6, "Ks3_5_10": 6, "Ic1_1_3": 4, "Ic1_3_5": 4, "Ic1_5_10": 5,
                    "Ks2_3_1": 4, "Ks2_5_3": 6, "Ks2_10_5": 6, "Ks4_3_1": 4, "Ks4_5_3": 6, "Ks4_10_5": 6, "Ic2_3_1": 4, "Ic2_5_3": 4, "Ic2_10_5": 5
            },
            "headway": { "Ks1_Ks3_1_3": 2, "Ks1_Ks3_3_5": 2, "Ks1_Ks3_5_10": 2, "Ks3_Ks1_1_3": 2, "Ks3_Ks1_3_5": 2, "Ks3_Ks1_5_10": 2,
                        "Ks1_Ic1_1_3": 2, "Ks1_Ic1_3_5": 2, "Ks1_Ic1_5_10": 2, "Ks3_Ic1_1_3": 2, "Ks3_Ic1_3_5": 2, "Ks3_Ic1_5_10": 2,
                        "Ic1_Ks1_1_3": 2, "Ic1_Ks1_3_5": 2, "Ic1_Ks1_5_10": 2, "Ic1_Ks3_1_3": 2, "Ic1_Ks3_3_5": 2, "Ic1_Ks3_5_10": 2,

                        "Ks2_Ks4_3_1": 2, "Ks2_Ks4_5_3": 2, "Ks2_Ks4_10_5": 2, "Ks4_Ks2_3_1": 2, "Ks4_Ks2_5_3": 2, "Ks4_Ks2_10_5": 2,
                        "Ks2_Ic2_3_1": 2, "Ks2_Ic2_5_3": 2, "Ks2_Ic2_10_5": 2, "Ks4_Ic2_3_1": 2, "Ks4_Ic2_5_3": 2, "Ks4_Ic2_10_5": 2,
                        "Ic2_Ks2_3_1": 2, "Ic2_Ks2_5_3": 2, "Ic2_Ks2_5_10": 2, "Ic2_Ks4_3_1": 2, "Ic2_Ks4_5_3": 2, "Ic2_Ks4_10_5": 2,
            
            },
            "prep": {"Ic2_10": 20},
            "stop":{"Ks1_1": 1, "Ks1_3": 1, "Ks1_5": 1, "Ks1_10": 1, "Ks3_1": 1, "Ks3_3": 1, "Ks3_5": 1, "Ks3_10": 1, "Ic1_1": 1, "Ic1_3": 1, "Ic1_5": 1, "Ic1_10": 1,
            "Ks2_1": 1, "Ks2_3": 1, "Ks2_5": 1, "Ks2_10": 1, "Ks4_1": 1, "Ks4_3": 1, "Ks4_5": 1, "Ks4_10": 1, "Ic2_1": 1, "Ic2_3": 1, "Ic2_5": 1, "Ic2_10": 1
            }}
    timetable = {"tau": taus,
                 "initial_conditions": {"Ks1_1": 0, "Ks3_1": 60, "Ic1_1": 30, "Ks2_10": 40, "Ks4_10": 100, "Ic2_10": 95},
                 "penalty_weights": {"Ks1_5": 0.9, "Ks3_5": 0.9, "Ic1_5": 0.9, "Ks2_3": 1, "Ks2_5": 1, "Ic2_3": 1.5},
                 "schedule": {"Ks1_1": 0, "Ks3_1": 60, "Ic1_1": 10, "Ks2_10": 40, "Ks4_10": 100, "Ic2_10": 95}
                }


    t_ref = "8:00"
  

    prob = create_linear_problem(train_set, timetable, d_max, cat="Integer")

    args = parser.parse_args()

    assert args.solve_quantum in ["", "sim", "real", "hyb", "cqm", "save_qubo"]

    if args.solve_lp != "":
        if "CPLEX_CMD" == args.solve_lp:
            print("cplex")
            path_to_cplex = r'/opt/ibm/ILOG/CPLEX_Studio_Community221/cplex/bin/x86-64_linux/cplex'
            solver =  pl.CPLEX_CMD(path=path_to_cplex)
        else:    
            solver = pl.getSolver(args.solve_lp)

        start_time = time.time()
        prob.solve(solver = solver)
        end_time = time.time()
        print_optimisation_results(prob, timetable, train_set, train_set["skip_station"], d_max, t_ref)

        print("optimisation, time = ", end_time - start_time, "seconds")
        check_count_vars(prob)
        print("objective", prob.objective.value())


    # QUBO creation an solution
    
    if args.solve_quantum in ["sim", "real", "hyb", "save_qubo"]:
        pdict = {
            "minimal_span": 10,
            "single_line": 10,
            "minimal_stay": 10,
            "track_occupation": 10,
            "switch": 10,
            "occupation": 10,
            "circulation": 4,
            "objective": 1,
        }
        bqm, qubo, interpreter = convert_to_bqm(prob, pdict)

    if args.solve_quantum == "save_qubo":
        print("..... QUBO size .....")
        print("QUBO variables", len(bqm.variables))
        print("quadratic terms", count_quadratic_couplings(bqm))
        print("linear terms", count_linear_fields(bqm))

        file = f"qubos/qubo_wisla_case1.pkl"
        with open(file, "wb") as f:
            pkl.dump(qubo[0], f)


    if args.solve_quantum in ["sim", "real", "hyb"]:
        sim_annealing_var = {"beta_range": (0.001, 10), "num_sweeps": 1000, "num_reads": 1000}
        real_anneal_var_dict = {"num_reads": 260, "annealing_time": 1300, "chain_strength": 4}
        print(f"{args.solve_quantum} annealing")
        start_time = time.time()
        sampleset = annealing(bqm, interpreter, args.solve_quantum, sim_anneal_var_dict=sim_annealing_var, real_anneal_var_dict=real_anneal_var_dict)
        t = time.time() - start_time
        print(f"{args.solve_quantum} time = ", t, "seconds")
        dict_list = get_results(sampleset, prob=prob)
        sample = get_best_feasible_sample(dict_list)
        sample.update({"comp_time_seconds": t})

        #print_results(dict_list)

    if args.solve_quantum == "cqm":
        cqm, interpreter = convert_to_cqm(prob)
        start_time = time.time()
        sampleset = constrained_solver(cqm)
        t = time.time() - start_time
        dict_list = get_results(sampleset, prob=prob)
        sample = get_best_feasible_sample(dict_list)
        sample.update({"comp_time_seconds": t})

        #print_results(dict_list)

    if args.solve_quantum in ["sim", "real", "hyb", "cqm"]:
        file = f"solutions_quantum/{args.solve_quantum}_wisla_case1.pkl"
        with open(file, "wb") as f:
            pkl.dump(sample, f)


