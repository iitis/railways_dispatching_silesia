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
    load_timetables,
    load_important_stations,
    load_data_paths,
    build_timetables,
    make_taus,
    make_timetable,
    make_train_set,
    print_optimisation_results,
    check_count_vars
)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Make variables to problem from dataframes, parameters of problem and solutions")
    parser.add_argument(
        "--stations",
        required=True,
        type=str,
        help="Path to important_station dictionary",
    )
    parser.add_argument(
        "--load", type=str, required=False, help="Path to trains dataframes dictionary"
    )
    parser.add_argument(
        "--paths",
        type=str,
        required=True,
        help="Path for data containing blocks passing times",
    )

    parser.add_argument(
        "--case",
        type=int,
        help="Case of railway problem choose: 0 (no distur.), 1: (one IC late), 2 (one IC late), 3 (all from Ty late), 4 (all laving KO late), 5 (14 trains late) 6 (as case 0) 7 (as case 5)",
        default=0,
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
        help="quantum or quantum inspired solver: 'sim' - D-Wave simulation, 'real' - D-Wave, 'hyb' - D-Wave hybrid via QUBO,  'cqm' - D-Wave hybrid cqm",
        default="",
    )

    subparsers = parser.add_subparsers(help="sub-command help")
    parser_build = subparsers.add_parser("build", help="Build dataframes from files")
    parser_build.add_argument(
        "-d", type=str, default=None, help="path for data containing timetables"
    )
    parser_build.add_argument(
        "-save", required=False, action="store_true", help="save built train dictionary"
    )
    args = parser.parse_args()
    if (args.load == None) and ("d" not in args):
        print(
            "Please provide data.\
            \n --load the trains dictonary with dataframe or \
            \n build a new one with the paths to -d timetable data."
        )
        exit(1)

    important_stations = load_important_stations(args.stations)
    data_paths = load_data_paths(args.paths)

    if args.load:
        train_dict = load_timetables(args.load)
    else:
        train_dict = build_timetables(args.d, args.save, important_stations, data_paths)

    taus = make_taus(train_dict, important_stations, r=0)  # r = 0 no rounding

    skip_stations = get_skip_stations(train_dict)

    train_set = make_train_set(
        train_dict, important_stations, data_paths, skip_stations
    )
    t_ref = "16:00"
    timetable = make_timetable(train_dict, important_stations, skip_stations, t_ref)

    # args.case == 0 no distrubrance

    d_max = 40
    if args.case == 1:
        delay = 12
        train = 14006
        timetable["initial_conditions"] = add_delay(
            timetable["initial_conditions"], train, delay
        )

    if args.case == 2:
        delay = 15
        train = 5312
        timetable["initial_conditions"] = add_delay(
            timetable["initial_conditions"], train, delay
        )

    if args.case == 3:
        delays = [15, 12, 13, 6, 21]
        trains = [94766, 40518, 41004, 44862, 4120]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], train, delays[i]
            )
            i = i + 1

    if args.case == 4:
        delays = [30, 12, 25, 5, 30]
        trains = [421009, 94611, 94113, 44717, 94717]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], train, delays[i]
            )
            i = i + 1

    if args.case == 5 or args.case == 7 or args.case == 8 or args.case == 9:
        delays = [30, 12, 18, 5, 30, 23, 3, 21, 35, 10, 25, 7, 5, 16]
        trains = [
            94766,
            26013,
            5312,
            40518,
            34319,
            14006,
            40150,
            41004,
            45101,
            4500,
            49317,
            64359,
            44862,
            73000,
        ]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], train, delays[i]
            )
            i = i + 1

    prob = create_linear_problem(train_set, timetable, d_max, cat=args.category)

    assert args.solve_quantum in ["", "sim", "real", "hyb", "cqm"]

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
        print_optimisation_results(prob, timetable, train_set, skip_stations, d_max, t_ref)
        print("............ case", args.case, ".......")

        print("optimisation, time = ", end_time - start_time, "seconds")
        check_count_vars(prob)
        print("objective x d_max  in [min]", prob.objective.value() * d_max)


    # QUBO creation an solution
    
    if args.solve_quantum in ["sim", "real", "hyb"]:
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
        bqm, qubo, interpreter = convert_to_bqm(prob, pdict)



    if args.solve_quantum in ["sim", "real", "hyb"]:
        sim_annealing_var = {"beta_range": (0.001, 10), "num_sweeps": 10, "num_reads": 2}
        real_anneal_var_dict = {"num_reads": 3996, "annealing_time": 250, "chain_strength": 4}
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
        file = f"solutions_quantum/{args.solve_quantum}_case{args.case}_{args.category}.pkl"
        with open(file, "wb") as f:
            pkl.dump(sample, f)


