from railway_solvers import *
from Qfile_solve import  constrained_solver

taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 6,
                                                                }, "stop": {"0_1_None": 1, "1_1_None": 1}, "res": 1}
timetable = {"tau": taus,
                "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
                "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1}}

d_max = 10
μ = 30

train_sets = {
    "skip_station": {
        0: [None],
        1: [None],
        2: [0],
    },
    "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
    "J": [0, 1, 2],
    "Jd": [[0, 1], [2]],
    "Josingle": [],
    "Jround": dict(),
    "Jtrack": {1: [[0, 1]]},
    "Jswitch": dict()
}

train_sets_rerouted = {
    "skip_station": {
        0: [None],
        1: [None],
        2: [0],
    },
    "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
    "J": [0, 1, 2],
    "Jd": [],
    "Josingle": [[1, 2], []],
    "Jround": dict(),
    "Jtrack": {1: [[0, 1]]},
    "Jswitch": dict()
}

prob = create_linear_problem(train_sets, timetable, d_max, μ)
cqm, interpreter = convert_to_cqm(prob)
file_name = f"annealing_results/cqm_default"

sampleset = constrained_solver(cqm)
store_result(file_name, sampleset, "cqm")

sampleset = interpreter(load_results(file_name))
dict_list = get_results(sampleset, "cqm", prob)
print("Best Sample ", get_best_fesible_sample(dict_list))

for l in dict_list:
    print(l)
