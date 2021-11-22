train_sets = {
    "skip_station": {
        0: None,
        1: None,
    },
    "Paths": {0: [0, 1], 1: [1, 0]},
    "J": [0, 1],
    "Jd": dict(),
    "Josingle": dict(),
    "Jround": {1: [[0,1]]},
    "Jtrack": dict(),
    "Jswitch": dict()
}

taus = {"pass": {"0_0_1": 4, "1_1_0": 8}, "prep": {"1_1": 2}, "stop":{"1_0": 0, "0_1": 0}}
timetable = {"tau": taus,
             "initial_conditions": {"0_0": 3, "1_1": 1},
             "penalty_weights": {"0_0": 2, "1_1": 0.5}}

d_max = 10
μ = 30
