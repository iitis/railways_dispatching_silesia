"""
1 ->                                       <- 2
...............................................
 [ A ]                              .  .    [ B ]
.....................................c.........
0 ->
"""

taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
        "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
        "stop": {"0_B": 1, "1_B": 1},
        "res": 1
        }

timetable = {"tau": taus,
             "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
             "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}


train_sets = {
    "skip_station": {2: "A"},
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
    "Josingle": {},
    "Jround": {},
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {},
    "add_swithes_at_s": ["B"]
}


train_sets = {
    "skip_station": {
        2: "A",
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": {},
    "Josingle": {("A", "B"): [[1,2]]},
    "Jround": {},
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
    "add_swithes_at_s": ["B"]
}

d_max = 10
