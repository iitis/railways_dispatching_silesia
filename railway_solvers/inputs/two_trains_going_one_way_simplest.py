"""
two trains, 0 and 1 are going one way A -> B test minimal span

    A                            B
 1 ->
 0 ->  --------------------------
"""


taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
        "blocks": {"0_1_A_B": 2, "1_0_A_B": 6},
        "stop": {"0_B": 1, "1_B": 1}, "res": 1}
timetable = {"tau": taus,
             "initial_conditions": {"0_A": 3, "1_A": 1},
             "penalty_weights": {"0_A": 2, "1_A": 0.5}}

train_sets = {
    "skip_station": {
        0: None,
        1: None,
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"]},
    "J": [0, 1],
    "Jd": {"A": {"B": [[0, 1]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": dict(),
    "Jswitch": dict()
}

d_max = 10
