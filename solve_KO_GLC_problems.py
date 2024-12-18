""" generic problems on KO -- CB --- RCB -- ZZ --- GLC line """
import pickle as pkl
import time
import pulp as pl
#from time import datetime

from data_formatting.data_formatting import (
    add_delay,
    get_skip_stations
)
from railway_solvers.railway_solvers import (
    create_linear_problem,

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
    count_vars,
    solve_on_quantum
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
        "--time_limit",
        type=float,
        help="time limit for linear solver",
        default=0,
    )
    parser.add_argument(
        "--solve_quantum",
        type=str,
        help="quantum or quantum inspired solver: 'sim' - D-Wave simulation, 'real' - D-Wave, 'bqm' - D-Wave hybrid via QUBO,  'cqm' - D-Wave hybrid cqm",
        default="",
    )

    parser.add_argument(
        "--min_t",
        type=int,
        help="minimal time parameter for cqm solver, lowest value is 5",
        default=5,
    )
    args = parser.parse_args()

    assert args.case in [1,2,3]
    # paths to files
    if args.case == 1:
        important_stations_path = "./data/KO_GLC/important_stations_KO_GLC.npz"
        data_paths = load_data_paths("./data/network_paths.ods")
        d = "./data/KO_GLC/trains_schedules_KO_GLC.csv"
    if args.case == 2:
        important_stations_path = "./data/KO_GLC/important_stations_KO_GLC_R.npz"
        data_paths = load_data_paths("./data/network_paths.ods")
        d = "./data/KO_GLC/trains_schedules_KO_RCB_ZZ_GLC.csv"
    if args.case == 3:
        important_stations_path = "./data/KO_GLC/important_stations_KO_GLC_R.npz"
        data_paths = load_data_paths("./data/network_paths.ods")
        d = "./data/KO_GLC/trains_schedules_KO_RCB_ZZ_GLC_v2.csv"

    important_stations = load_important_stations(important_stations_path)
    train_dict = build_timetables(d, False, important_stations, data_paths)
    #print(train_dict)
    taus = make_taus(train_dict, important_stations, r=0)  # r = 0 no rounding
    skip_stations = get_skip_stations(train_dict)
    train_set = make_train_set(
        train_dict, important_stations, data_paths, skip_stations
    )
    print(train_set.keys())
    #print(train_set["Paths"])
    print(train_set["J"])
    t_ref = "14:00"
    assert args.solve_quantum in ["", "sim", "real", "bqm", "cqm"]

    # input
    d_max = 40
    disturbances = {}

    disturbances[0] = {}
    if args.case != 3:
        disturbances[1] = dict({4602:2})
        disturbances[2] = dict({6401:3, 4604:13})
        disturbances[3] = dict({1:2, 3:2, 5:7})
        disturbances[4] = dict({2:2, 4:2, 6405:3, 6407:3})
        disturbances[5] = dict({1:5, 2:3, 3:7, 4:2, 5:1, 6401:2})
        disturbances[6] = dict({3:7, 4:2, 5:1, 23: 6, 1:6, 6407:2, 101: 4, 4602: 7})
        disturbances[7] = dict({1:5, 11:3, 21:3, 25:2, 2:4, 4:6, 6:6, 8:3, 10:3, 22:6, 24:1})
        disturbances[8] = dict({1:3, 2:5, 3:7, 4:25, 5:8, 6:12, 7:17, 23:4, 25:3, 24:8, 10:4, 6401:3, 6403:7, 101:8})
        disturbances[9] = dict({2:3, 4602:1, 4:10, 102:2, 6:15, 8:7, 4604:4, 10:1, 12:7, 1:10, 101:8, 3:2, 6401:6, 5:15, 7:1, 103:30, 9:7, 6403:8})
        disturbances[10] = dict({i: i%3 for i in train_set["J"]})
        disturbances[11] = dict({i: i%10 for i in train_set["J"]})
    else:
        disturbances[1] = dict({2:18})
        disturbances[2] = dict({2:36, 4602: 20})
        disturbances[3] = dict({101:18, 1:29, 3:25})
        disturbances[4] = dict({101:18, 1:29, 3:25, 5:15, 2:18})
        disturbances[5] = dict({101:18, 1:29, 3:25, 5:15, 2:36, 4602: 20, 9:12})
        disturbances[6] = dict({101:18, 1:29, 3:25, 5:15, 2:36, 4602: 20, 9:12, 103:15, 10:50, 4606:30})
        disturbances[7] = dict({2:50, 4602: 32, 4:10, 102:5, 1:12, 101:10 })
        disturbances[8] = dict({2:90, 4602: 72, 4:72, 102:45, 4604:10, 101:47,  6401: 35, 3:20})
        disturbances[9] = dict({2:90, 4602:72, 4:72, 102:45, 4604:10, 101:47, 6401: 35, 6403:20, 5:25, 103:30, 3:60, 10:25})
        disturbances[10] = dict({1:29, 2:36, 4602: 20, 9:12, 4606:30, 102:45, 101:47, 6401: 35, 6403:20, 5:25, 103:30, 3:60, 4604:10, 10:25})
        disturbances[11] = dict({2:92, 4602:70, 4:72, 102:46, 101:45, 6401:33, 6403:20, 5:25, 103:28, 3:59, 4604:12, 10:25})
    
    print("n.o. trains", len(train_set["J"]))

    # QUBO prameters if necessary
    pdict = {}
    if args.solve_quantum in ["sim", "real", "bqm"]:
        p = 2.5
        pdict = {
            "minimal_span": p,
            "single_line": p,
            "minimal_stay": p,
            "track_occupation": p,
            "switch": p,
            "occupation": p,
            "circulation": p,
            "objective": 1,
        }


    results = {}
    results["method"] = args.solve_lp
    results["d_max"] = d_max
    results["case"] = args.case

    for k in disturbances:
        print("n.o. problem", k)
        dist = disturbances[k]
        timetable = make_timetable(train_dict, important_stations, skip_stations, t_ref)
        print(timetable["initial_conditions"])
        print("..............")
        print(timetable["schedule"])
        for i in dist:
            if i not in train_set["J"]:
                print(i)
            assert i in train_set["J"]
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
                # TODO user can add custom path
                path_to_cplex = r'/home/ludmila/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex'
                if args.time_limit == 0:
                    solver =  pl.CPLEX_CMD(path=path_to_cplex)
                else:
                    solver = pl.CPLEX_CMD(path=path_to_cplex, timeLimit = args.time_limit)
            else: 
                if args.time_limit == 0:   
                    solver = pl.getSolver(args.solve_lp)
                else:
                    solver = pl.getSolver(args.solve_lp, timeLimit = args.time_limit)

            start_time = time.time()
            prob.solve(solver = solver)
            end_time = time.time()
            visualize = False

            if visualize:
                reference_time = datetime(year = 2020, month = 1, day = 1, hour = int(t_ref[0:2]), minute = int(t_ref[3:5]))
                data4diagrams = print_optimisation_results(prob, timetable, train_set, taus, skip_stations, d_max, reference_time)
                print(data4diagrams)

            result["objective"] = prob.objective.value() * d_max
            result["comp_time_seconds"] = end_time - start_time
            result["feasible"] = True
            results["brolen_constraints"] = 0
            check_count_vars(prob)

        elif args.solve_quantum in ["sim", "real", "bqm", "cqm"]:
            sample = solve_on_quantum(prob, args.solve_quantum, pdict, minimum_time_limit= args.min_t)
            result.update(sample)
            result["broken_constraints"] = constraints - result["feas_constraints"][1]
            print("broken constraints", result["broken_constraints"])

        print(".............")
        print(k)
        print(result)
        results[k] = result
    results["samples"] = k+1

    print(results)

    print("save ... ")

    try: 
        p = result["properties"]["minimum_time_limit_s"]
        print("minimal time limit", p)
    except:
        p = ""
    if args.time_limit == 0:
        file = f"results_KO_GLC/results{p}_{args.solve_lp}_{args.solve_quantum}_{args.case}_{args.category}.pkl"
    else:
        file = f"results_KO_GLC/results{p}_{args.solve_lp}_ilp_t_lim{args.time_limit}_{args.solve_quantum}_{args.case}_{args.category}.pkl"
    with open(file, "wb") as f:
        pkl.dump(results, f)
