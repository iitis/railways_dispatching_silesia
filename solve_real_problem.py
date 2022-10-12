import pickle as pkl
import numpy as np
import pandas as pd
import time

from data_formatting.data_formatting import (get_initial_conditions, get_J,
                                             get_jround, get_Paths,
                                             get_schedule, get_taus_headway,
                                             get_taus_pass, get_taus_prep,
                                             get_taus_stop, jd, josingle,
                                             jswitch, jtrack, make_weights,
                                             timetable_to_train_dict,
                                             update_all_timetables,
                                             add_delay)
from railway_solvers.railway_solvers import (create_linear_problem,
                                            delay_and_acctual_time,
                                            impact_to_objective)


def load_timetables(timetables_path):
    with open(timetables_path.load, "rb") as file:
        train_dict = pkl.load(file)
    return train_dict


def load_important_stations(important_station_path):
    return np.load(important_station_path, allow_pickle=True)["arr_0"][()]


def load_data_paths(data_paths_path):
    return pd.read_excel(data_paths_path, engine="odf")


def build_timetables(args, important_stations, data_paths):
    data = pd.read_csv(args.d, sep=";", engine="python")
    train_dicts = timetable_to_train_dict(data)
    train_dicts = update_all_timetables(
        train_dicts, data_paths, important_stations, save=args.save
    )
    return train_dicts


def make_taus(train_dict, important_stations, r):
    taus = {}
    taus["pass"] = get_taus_pass(train_dict)
    taus["headway"] = get_taus_headway(train_dict, important_stations, r)
    taus["prep"] = get_taus_prep(train_dict, important_stations)
    taus["stop"], prep_extra = get_taus_stop(train_dict, important_stations)
    taus["prep"].update(prep_extra)
    taus["res"] = r
    return taus


def make_timetable(train_dict, important_stations, skip_stations, t1="16:00", taus=None):
    timetable = {}
    if taus == None:
        taus = make_taus(train_dict, important_stations, 1)
    timetable["tau"] = taus
    timetable["initial_conditions"] = get_initial_conditions(train_dict, t1)
    timetable["penalty_weights"] = make_weights(
        train_dict, skip_stations, stopping=1, fast=1.5, express=1.75, empty=0
    )
    timetable["schedule"] = get_schedule(train_dict, t1)
    return timetable


def make_train_set(train_dict, important_stations, data_path, skip_stations):
    train_set = {}
    train_set["skip_station"] = skip_stations
    train_set["Paths"] = get_Paths(train_dict)
    train_set["J"] = get_J(train_dict)
    train_set["Jd"] = jd(train_dict, important_stations)
    train_set["Josingle"] = josingle(train_dict, important_stations)
    train_set["Jround"] = get_jround(train_dict, important_stations)
    train_set["Jtrack"] = jtrack(train_dict, important_stations)
    train_set["Jswitch"] = jswitch(train_dict, important_stations, data_path)
    return train_set


def print_optimisation_results(prob, timetable, train_set, d_max):
    print("xxxxxxxxxxx  OUTPUT TIMETABLE  xxxxxxxxxxxxxxxxx")
    print("reference_time", t1)
    for j in train_set["J"]:
        print("..............")
        print("train", j)
        for s in train_set["Paths"][j]:
            if j in skip_stations and s == skip_stations[j]: # TODO improve if
                0
            else:
                delta_obj = impact_to_objective(prob, timetable, j, s, d_max)
                delay, conflict_free = delay_and_acctual_time(train_set, timetable, prob, j, s)
                try: 
                    sched = timetable["schedule"][f"{j}_{s}"]
                    print(s, "secondary delay", delay, "conflict free time", conflict_free, "impact to obj.", delta_obj, "schedule", sched)
                except:
                    print(s, "secondary delay", delay, "conflict free time", conflict_free, "impact to obj.", delta_obj)


def check_count_vars(prob):
    """
    counts n.o. vars and checks if bool vars are 0 or 1
    TODO it can be done better, 
    """
    order_vars = 0
    for v in prob.variables():
        if "z_" in str(v) or "y_" in str(v):
            assert v.varValue in [0.0, 1.0]
            order_vars += 1
    print("n.o. integer_vars", order_vars)
    print("n.o. order vars", len(prob.variables()) - order_vars)  


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Make variables to problem from dataframes")
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
    subparsers = parser.add_subparsers(help="sub-command help")
    parser_build = subparsers.add_parser("build", help="Build dataframes from files")
    parser_build.add_argument(
        "-d", type=str, default=None, help="path for data containing timetables"
    )
    parser_build.add_argument(
        "-save", required=False, action="store_true", help="save built train dictionary"
    )
    args = parser.parse_args()
    print(args)
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
        train_dict = build_timetables(args, important_stations, data_paths)


    t1 = "16:00"
    taus = make_taus(train_dict, important_stations, t1)
    
    skip_stations = {94766: "KO(STM)", 421009: "KO", 40518: "KO(STM)", 34319: "KO", 343199: "KO(STM)",
                     40673: "GLC", 54101: "KO", 541019: "KO(IC)", 44862: "KO(STM)", 40675: "GLC",
                     }
    train_set = make_train_set(train_dict, important_stations, data_paths, skip_stations)
    timetable = make_timetable(train_dict, important_stations, skip_stations, t1)


    case = 5

    # case 0 no distrubrance

    d_max = 40
    if case == 1:
        delay = 12
        train = 14006
        timetable["initial_conditions"] = add_delay(timetable["initial_conditions"], train, delay)

    if case == 2:
        delay = 15
        train = 5312
        timetable["initial_conditions"] = add_delay(timetable["initial_conditions"], train, delay)


    if case == 3:
        delays = [15, 12, 13, 6, 21]
        trains = [94766, 40518, 41004, 44862, 4120]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(timetable["initial_conditions"], train, delays[i])
            i = i+1


    if case == 4:
        delays = [30, 12, 25, 5, 30]
        trains = [421009, 94611, 94113, 44717, 94717]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(timetable["initial_conditions"], train, delays[i])
            i = i+1

    if case == 5:
        delays = [30, 12, 17, 5, 30, 22, 3, 20, 35, 10, 25, 7, 5, 15]
        trains = [94766, 26013, 5312, 40518, 34319, 14006, 40150, 41004, 45101, 4500, 49317, 64359, 44862, 73000]
        i = 0
        for train in trains:
            timetable["initial_conditions"] = add_delay(timetable["initial_conditions"], train, delays[i])
            i = i+1


    prob = create_linear_problem(train_set, timetable, d_max)


    start_time = time.time()
    prob.solve()
    print("optimisation, time = ", time.time() - start_time, "seconds")

    check_count_vars(prob)
    print_optimisation_results(prob, timetable, train_set, d_max)
    print("............")
    print("objective", prob.objective.value())




