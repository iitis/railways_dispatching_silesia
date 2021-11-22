taus = {"pass": {"0_0_1": 4, "1_0_1": 4}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 2,
                                                     }, "stop": {"0_1": 1, "1_1": 1}, "res": 2}
timetable = {"tau": taus,
             "initial_conditions": {"0_0": 1, "1_0": 1},
             "penalty_weights": {"0_0": 2, "1_0": 0.5}}

train_sets = {
    "skip_station": {
        0: None,
        1: None,
    },
    "Paths": {0: [0, 1], 1: [0, 1]},
    "J": [0, 1],
    "Jd": dict(),
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {1: [[0, 1], []]},
    "Jswitch": {1: [[0, 0, 0, 1], [1,1,0,1]]},
    "add_swithes_at_s": [1]
    
d_max = 10
μ = 30
