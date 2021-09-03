import sys

sys.path.append('../src')


from linear_solver import *

taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8, "2_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_None" : 1, "1_1_None" : 1}, "res": 1}
timetable = {"tau": taus,
              "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
              "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}

def test_linear_solver():


    d_max = 10
    μ = 30

    train_sets = {
    "skip_station": {
        0: [None],
        1: [None],
        2: [0],
    },
    "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
    "J": [0,1,2],
    "Jd": [[0,1], [2]],
    "Josingle": [],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }

    train_sets_rerouted = {
    "skip_station": {
        0: [None],
        1: [None],
        2: [0],
    },
    "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
    "J": [0,1,2],
    "Jd": [],
    "Josingle": [[1,2], []],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }

    prob = solve_linear_problem(train_sets, timetable, d_max, μ)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_0_1":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 5
        if v.name == "Delays_2_1":
            delay = v.varValue
            assert delay == 0

    assert prob.objective.value() == 0.5


    prob = solve_linear_problem(train_sets_rerouted, timetable, d_max, μ)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_0_1":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 1
        if v.name == "Delays_2_1":
            delay = v.varValue
            assert delay == 3

    assert prob.objective.value() == 0.4


test_linear_solver()
print("tests done")
