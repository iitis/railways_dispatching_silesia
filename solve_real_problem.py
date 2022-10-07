import argparse

import numpy as np

import pandas as pd
from data_formatting.data_formatting import (
    get_jround,
    get_trains_pair9,
    jd,
    josingle,
    jswitch,
    jtrack,
    timetable_to_train_dict,
    update_all_timetables,
)

# from railway_solvers.railway_solvers import (create_linear_problem,
#                                              delay_and_acctual_time,
#                                              delay_varibles,
#                                              impact_to_objective,
#                                              order_variables,
#                                              solve_linear_problem)

# TODO we should have a path to input file as an argument

# TODO please produce Js and \taus from in the form analogical to, all functions should be in data_formatting.data_formatting

parser = argparse.ArgumentParser("Make variables to problem for dataframes")
parser.add_argument(
    "--stations", required=True, type=str, help="Path to important_station dictionary"
)
parser.add_argument(
    "--load", type=str, required=False, help="Path to trains dataframes dictionary"
)
subparsers = parser.add_subparsers(help="sub-command help")
parser_build = subparsers.add_parser("build", help="Build dataframes from files")
parser_build.add_argument("-d", type=str, help="path for data containing timetables")
parser_build.add_argument(
    "-p", type=str, help="path for data containing blocks passing times"
)
parser_build.add_argument(
    "-sava_data", required=False, type=str, help="save built train dictionary"
)


# parser.add_argument("--build", type=str, required=False, help="Path to timetables csv")

args = parser.parse_args()
print(args)
if (not args.load) and (not all([args.p, args.d])):
    print(
        "Please provide data.\
        \n --load the trains dictonary with dataframe or \
        \n build a new one with -d timetable data and -p data for passing time"
    )
    exit(1)

# parser = argparse.ArgumentParser()
# parser.add_argument("--trains_dict", type=str, required=False)

# parser.add_argument("--data", type=str, required=False)
# parser.add_argument("--data_paths", type=str, required=False)
# parser.add_argument("--important_stations", type=str, required=False)

# args = parser.parse_args()
# data = arg.data
# data_path = arg.data_path
# important_stations = arg.important_stations
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
