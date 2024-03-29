""" close to real problems on metropolitan network """
import pickle as pkl
import time
import pulp as pl
from datetime import datetime
import pandas as pd


from data_formatting.data_formatting import (
    add_delay,
    get_skip_stations
)
from railway_solvers.railway_solvers import (
    convert_to_bqm,
    create_linear_problem
)

from helpers import (
    load_important_stations,
    load_data_paths,
    build_timetables,
    make_taus,
    make_timetable,
    make_train_set,
    print_optimisation_results,
    check_count_vars,
    solve_on_quantum
)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("cases of the problem, parameters of problem and solutions")

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

    parser.add_argument(
        "--min_t",
        type=int,
        help="minimal time parameter for cqm solver, lowest value is 5",
        default = 5,
    )

    parser.add_argument(
        "--runs",
        type=int,
        help="number of runs",
        default = 1,
    )

    parser.add_argument(
        "--penalty",
        type=float,
        help="pval for bqm",
        default = 1.,
    )

    parser.add_argument(
        "--show_timetable",
        type=int,
        help="show timetable of the solution",
        default=False,
    )     

    args = parser.parse_args()
    
    assert args.case in [0,1,2,3,4,5,6,7,8,9]

    # paths to files
    data_paths = load_data_paths("./data/network_paths.ods")    
    if args.case in (0,1,2,3):
        important_stations_path = "./data/important_stations.npz"  
        block_schedule = "./data/trains_schedules.csv"

    if args.case in (4,5):
        important_stations_path = "./data/important_stations_Gt.npz"
        block_schedule = "./data/trains_schedules_Gt.csv"

    if args.case == 6:
        important_stations_path = "./data/important_stations.npz"
        block_schedule = "./data/trains_schedules_1track.csv"

    if args.case in (7,8,9):
        important_stations_path = "./data/important_stations_Gt.npz"
        block_schedule = "./data/trains_schedules_1track_Gt.csv"
    

    important_stations = load_important_stations(important_stations_path)
    train_dict = build_timetables(block_schedule, True, important_stations, data_paths)

    taus = make_taus(train_dict, important_stations, r=0)  # r = 0 no rounding

    skip_stations = get_skip_stations(train_dict)

    train_set = make_train_set(
        train_dict, important_stations, data_paths, skip_stations
    )
    t_ref = "16:00"
    timetable = make_timetable(train_dict, important_stations, skip_stations, t_ref)
    reference_time = datetime(year = 2020, month = 1, day = 1, hour = int(t_ref[0:2]), minute = int(t_ref[3:5]))

    # args.case == 0 no distrubrance

    d_max = 40
    if args.case == 1:
        delay = 12
        train = 14006
        timetable["initial_conditions"] = add_delay(
            timetable["initial_conditions"], train, delay
        )


    if args.case == 2:
        delays = [15, 12, 13, 6, 21]
        trains = [94766, 40518, 41004, 44862, 4120]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], train, delays[i]
            )
            i = i + 1


    if args.case in (3, 5, 6, 7):
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
    
    if args.case == 8:
        delays = [28, 10, 12, 7, 30, 13, 3, 10, 28, 30, 11, 5, 7]
        trains = [
            94766,
            26013,
            42009,
            5312,
            34319,
            14006,
            94611,
            40150,
            41004,
            45101,
            94113,
            40673,
            54101,
        ]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(
                timetable["initial_conditions"], train, delays[i]
            )
            i = i + 1

    if args.case == 9:
        delays = [30, 11, 15, 19, 5, 28, 21, 4, 21, 34, 11, 25, 7, 5, 5]
        trains = [
            94766,
            26013,
            42009,
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

    assert args.solve_quantum in ["", "sim", "real", "bqm", "cqm"]

    if args.solve_lp != "":
        if "CPLEX_CMD" == args.solve_lp:
            print("cplex")
            # TODO user can add custom path
            path_to_cplex = r'/home/ludmila/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex'
            solver =  pl.CPLEX_CMD(path=path_to_cplex)
        else:    
            solver = pl.getSolver(args.solve_lp)
        start_time = time.time()
        prob.solve(solver = solver)
        end_time = time.time()
        if args.show_timetable:
            data4diagrams = print_optimisation_results(prob, timetable, train_set, taus, skip_stations, d_max, reference_time)
            file_sched = f"solutions_quantum/data4diagrams/{args.solve_lp}_case{args.case}_{args.category}.pkl"
            with open(file_sched, "wb") as f:
                pkl.dump(data4diagrams, f)

        print("............ case", args.case, ".......")
        print("optimisation, time = ", end_time - start_time, "seconds")
        check_count_vars(prob)
        print("objective", prob.objective.value())
        print("objective x d_max  in [min]", prob.objective.value() * d_max)

    # QUBO paramters if necessary
    pdict = {}
    if args.solve_quantum in ["sim", "real", "bqm"]:
        penalty = args.penalty
        pdict = {
            "minimal_span": penalty,
            "single_line": penalty,
            "minimal_stay": penalty,
            "track_occupation": penalty,
            "switch": penalty,
            "occupation": penalty,
            "circulation": penalty,
            "objective": 1,
        }
        #bqm, qubo, interpreter = convert_to_bqm(prob, pdict)

    if args.solve_quantum in ["sim", "real", "bqm", "cqm"]:

        if args.solve_quantum in ["cqm", "bqm"]:
            p = args.min_t
        else:
            p = ""
        if args.solve_quantum == "cqm":
            file = f"solutions_quantum/{args.solve_quantum}{p}_case{args.case}_{args.category}.pkl"
        else:
            file = f"solutions_quantum/{args.solve_quantum}{p}_{args.penalty}_case{args.case}_{args.category}.pkl"

        if args.show_timetable:
            data = pd.read_pickle(file)
            data4diagrams = {}
            for i in range(args.runs):
                data4diagrams[i+1] = print_optimisation_results(prob, timetable, train_set, taus, train_set["skip_station"], d_max, reference_time, data[i+1]["sample"])
                if args.solve_quantum == "cqm":
                    file_sched = f"solutions_quantum/data4diagrams/{args.solve_quantum}{p}_case{args.case}_{args.category}.pkl"
                else:
                    file_sched = f"solutions_quantum/data4diagrams/{args.solve_quantum}{p}_{args.penalty}_case{args.case}_{args.category}.pkl"

                with open(file_sched, "wb") as f:
                    pkl.dump(data4diagrams, f)
        
        else:
            samples = dict()
            for i in range(args.runs):
                samples[i+1] = solve_on_quantum(prob, args.solve_quantum, pdict, minimum_time_limit = args.min_t)
            

            with open(file, "wb") as f:
                pkl.dump(samples, f)
            
