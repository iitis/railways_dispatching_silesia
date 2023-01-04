"""
At station B train 0 terminates and turns intro train 1 that starts there

....0 -> ..................................0 <-> 1.......
 [ A ]                                      [  B  ]

"""

train_sets = {
    "Paths": {0: ["A", "B"], 1: ["B", "A"]},
    "J": [0, 1],
    "Jd": {},
    "Josingle": {},
    "Jround": {"B": [[0,1]]},
    "Jtrack": {},
    "Jswitch": {}
}

taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2},
        "stop":{"1_A": 0, "0_B": 0}}
timetable = {"tau": taus,
             "initial_conditions": {"0_A": 3, "1_B": 1},
             "penalty_weights": {"0_A": 2, "1_B": 0.5}}

d_max = 10
