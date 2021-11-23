train_sets = {
    "skip_station": {
        0: None,
        1: None,
    },
    "Paths": {0: [0, 1], 1: [1, 0]},
    "J": [0, 1],
    "Jd": dict(),
    "Josingle": {(0,1): [[0,1]]},
    "Jround": dict(),
    "Jtrack": dict(),
    "Jswitch": {0: [{0: "out", 1: "in"}], 1: [{0: "in", 1: "out"}]}
}

taus = {"pass": {"0_0_1": 4, "1_1_0": 8}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 6,
                                                     }, "stop": {"0_1": 1, "1_0": 1}, "res": 1}
timetable = {"tau": taus,
             "initial_conditions": {"0_0": 3, "1_1": 1},
             "penalty_weights": {"0_0": 2, "1_1": 0.5}}

d_max = 10
μ = 30
