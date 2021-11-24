taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 6
                                                                    }, "stop": {"0_1": 1, "1_1": 1}, "res": 1}
timetable = {"tau": taus,
             "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
             "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1}}


train_sets = {
    "skip_station": {
        0: None,
        1: None,
        2: 0,
    },
    "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
    "J": [0, 1, 2],
    "Jd": {0: {1: [[0, 1]]}, 1: {0: [[2]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {1: [[0, 1]]},
    "Jswitch": dict(),
    "add_swithes_at_s": [1]
}

train_sets_rerouted = {
    "skip_station": {
        0: None,
        1: None,
        2: 0,
    },
    "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
    "J": [0, 1, 2],
    "Jd": dict(),
    "Josingle": {(0,1): [[1,2]]},
    "Jround": dict(),
    "Jtrack": {1: [[0, 1]]},
    "Jswitch": {0: [{1:"out", 2:"in"}], 1: [{1:"in", 2:"out"}]},
    "add_swithes_at_s": [1]
}

d_max = 10
