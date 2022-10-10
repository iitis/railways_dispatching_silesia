import numpy as np
import pickle as pkl
import pandas as pd
from data_formatting.data_formatting import (
    get_jround,
    get_J,
    get_trains_pair9,
    jd,
    josingle,
    jswitch,
    jtrack,
    timetable_to_train_dict,
    update_all_timetables,
    get_taus_pass,
    get_taus_prep,
    get_taus_stop,
    make_weights
)
from data_formatting.data_formatting.make_J_taus import get_taus_headway
from data_formatting.data_formatting.utils import get_Paths, get_initial_conditions

# from railway_solvers.railway_solvers import (create_linear_problem,
#                                              delay_and_acctual_time,
#                                              delay_varibles,
#                                              impact_to_objective,
#                                              order_variables,
#                                              solve_linear_problem)

# TODO we should have a path to input file as an argument

# TODO please produce Js and \taus from in the form analogical to, all functions should be in data_formatting.data_formatting

def load_timetables(timetables_path):
    with open(timetables_path.load, 'rb') as file:
        train_dict = pkl.load(file)
    return train_dict

def load_important_stations(important_station_path):
    return np.load(important_station_path,allow_pickle=True)['arr_0'][()]

def load_data_paths(data_paths_path):
    return pd.read_excel(data_paths_path, engine="odf")

def build_timetables(args,important_stations,data_paths):
    data = pd.read_csv(args.d, sep = ";")
    train_dicts = timetable_to_train_dict(data)
    train_dicts = update_all_timetables(train_dicts,data_paths,important_stations,save = args.save)
    train_dict = {}
    return train_dict

def make_taus(train_dict,important_stations,r):
    taus ={}
    taus["pass"] = get_taus_pass(train_dict)
    taus["headway"] = get_taus_headway(train_dict,important_stations,r)
    taus["prep"] = get_taus_prep(train_dict)
    taus["stop"],prep_extra= get_taus_stop(train_dict)
    taus["prep"].update(prep_extra)
    taus["res"] = r
    return taus

def make_timetable(train_dict,important_stations,taus=None):
    timetable = {}
    if taus != None:
        timetable["taus"] = make_taus(train_dict,important_stations)
    else:
        timetable["taus"] = taus
    timetable["initial_conditions"] = get_initial_conditions(train_dict)
    timetable["penalty_weights"] = make_weights(train_dict, stopping=1, fast=1.5, express=1.75, empty=0)
    return timetable


def make_train_set(train_dict,important_stations,data_path):
    train_set= {}
    train_set["Paths"] = get_Paths(train_dict)
    train_set["J"] = get_J(train_dict)
    train_set["Jd"] = jd(train_dict,important_stations)
    train_set["Josingle"] = josingle(train_dict,important_stations)
    train_set["Jround"] = get_jround(train_dict,important_stations)
    train_set["Jtrack"] = jtrack(train_dict,important_stations)
    train_set["Jswitch"] = jswitch(train_dict,important_stations,data_path)

    return train_set



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Make variables to problem from dataframes")
    parser.add_argument(
        "--stations", required=True, type=str, help="Path to important_station dictionary"
    )
    parser.add_argument(
        "--load", type=str, required=False, help="Path to trains dataframes dictionary"
    )
    parser.add_argument(
        "--p", type=str, required=True, help="Path for data containing blocks passing times"
    )
    subparsers = parser.add_subparsers(help="sub-command help")
    parser_build = subparsers.add_parser("build", help="Build dataframes from files")
    parser_build.add_argument("-d", type=str, help="path for data containing timetables")
    parser_build.add_argument(
        "-save", required=False, action="store_true", help="save built train dictionary"
    )
    args = parser.parse_args()

    if (not args.load) and (not args.d):
        print(
            "Please provide data.\
            \n --load the trains dictonary with dataframe or \
            \n build a new one with the paths to -d timetable data."
        )
        exit(1)

    important_stations = load_important_stations(args.station)
    data_paths = load_data_paths(args.p)

    if args.load:
        train_dict = load_timetables(args.load)
    else:
        train_dict = build_timetables(args,important_stations)

    taus = make_taus(train_dict,important_stations)
    timetable = make_timetable(train_dict,important_stations)
    train_set = make_train_set(train_dict,important_stations,data_paths)


"""
    taus = {
        "pass": {
            "21_A_B": 4,
            "22_A_B": 8,
            "21_B_C": 4,
            "22_B_C": 8,
            "23_C_B": 6,
            "23_B_A": 6,
            "24_C_D": 3,
            "25_D_C": 3,
        },
        "headway": {"21_22_A_B": 2, "22_21_A_B": 6, "21_22_B_C": 2, "22_21_B_C": 6},
        "stop": {"21_B": 1, "22_B": 1, "21_C": 1, "23_B": 1},
        "prep": {"23_C": 3},
        "res": 1,
    }
    timetable = {
        "tau": taus,
        "initial_conditions": {
            "21_A": 6,
            "22_A": 1,
            "23_C": 26,
            "24_C": 25,
            "25_D": 28,
        },
        "penalty_weights": {
            "21_B": 2,
            "22_B": 0.5,
            "21_A": 2,
            "22_A": 0.5,
            "23_B": 0.8,
            "24_C": 0.5,
            "25_D": 0.5,
        },
    }

    train_sets = {
        "Paths": {
            21: ["A", "B", "C"],
            22: ["A", "B", "C"],
            23: ["C", "B", "A"],
            24: ["C", "D"],
            25: ["D", "C"],
        },
        "J": [21, 22, 23, 24, 25],
        "Jd": {"A": {"B": [[21, 22]]}, "B": {"C": [[21, 22]]}},
        "Josingle": {("C", "D"): [[24, 25]]},
        "Jround": {"C": [[22, 23]]},
        "Jtrack": {"B": [[21, 22]], "C": [[21, 24], [22, 23]]},
        "Jswitch": {
            "B": [{21: "out", 22: "out"}, {21: "in", 22: "in"}],
            "C": [
                {23: "out", 24: "out"},
                {22: "in", 24: "out"},
                {22: "in", 23: "out"},
                {21: "in", 24: "out"},
            ],
            "D": [{24: "in", 25: "out"}],
        },
    }
    """
