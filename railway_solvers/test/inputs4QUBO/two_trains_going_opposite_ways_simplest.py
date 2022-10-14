"""
Two trains going opposite direction on single track line
and swithes constrain

stations - [ A ]

swith - c

tracks - ......


..........                                        .. <- 1 ...
  [ A ]    .                                     .    [  B ]
..0 -> .... c ................................  c  ..........

"""
train_sets = {
    "Paths": {0: ["A", "B"], 1: ["B", "A"]},
    "J": [0, 1],
    "Jd": dict(),
    "Josingle": {("A","B"): [[0,1]]},
    "Jround": dict(),
    "Jtrack": dict(),
    "Jswitch": {"A": [{0: "out", 1: "in"}], "B": [{0: "in", 1: "out"}]}
}

taus = {"pass": {"0_A_B": 4, "1_B_A": 8},
        "stop": {"0_B": 1, "1_A": 1}, "res": 1}
timetable = {"tau": taus,
             "initial_conditions": {"0_A": 3, "1_B": 1},
             "penalty_weights": {"0_A": 2, "1_B": 0.5}}

d_max = 10
