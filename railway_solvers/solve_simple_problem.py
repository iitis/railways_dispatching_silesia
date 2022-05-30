#!/usr/bin/env python3

import pickle as pk
import numpy as np
from railway_solvers import earliest_dep_time, impact_to_objective, return_delay_and_acctual_time, solve_linear_problem




def toy_problem_variables(train_sets, timetable, d_max):
    prob = solve_linear_problem(train_sets, timetable, d_max)
    S = train_sets["Paths"]

    print("d_1, t_1", return_delay_and_acctual_time(S, timetable, prob, 0, "A"))
    print("d_2, t_2", return_delay_and_acctual_time(S, timetable, prob, 1, "A"))
    print("d_3, t_3", return_delay_and_acctual_time(S, timetable, prob, 2, "B"))
    print(
        "d_1', t_1'",
        return_delay_and_acctual_time(
            S,
            timetable,
            prob,
            0,
            "B"))

    print("impact to objective t_1", impact_to_objective(
        prob, timetable, 0, "A", d_max))
    print("impact to objective t_2", impact_to_objective(
        prob, timetable, 1, "A", d_max))
    print("impact to objective t_3", impact_to_objective(
        prob, timetable, 2, "B", d_max))


"""
                                        <- 2
...............................................
 [ A ]                             .   .   [ B ]
.....................................c.........
0 ->
1 ->
"""

taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
        "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
        "stop": {"0_B": 1, "1_B": 1},
        "res": 1
        }

timetable = {"tau": taus,
             "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
             "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

d_max = 10

train_sets = {
    "skip_station": {
        2: "A",  # we do not count train 2 leaving A
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": dict(),
    "add_swithes_at_s": ["B"]
}

#rerouting

"""
1 ->                                       <- 2
...............................................
 [ A ]                             .   .  [ B ]
.....................................c.........
0 ->
"""


train_sets_rerouted = {
    "skip_station": {
        2: "A",
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": dict(),
    "Josingle": {("A", "B"): [[1,2]]},
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
    "add_swithes_at_s": ["B"]
}

d_max = 10


####  liner solver ####

if True:
    toy_problem_variables(train_sets, timetable, d_max)
    toy_problem_variables(train_sets_rerouted, timetable, d_max)
    print("   ############   Done linear solver  #########")

#####   Q matrix generation #########
