import sys

sys.path.append('../src')


from linear_solver import *

def test_linear_solver():

    d_max = 10
    μ = 30


    S = {
        0: [0,1],
        1: [0,1],
        2: [1,0]
    }


    not_considered_station = {
        0: None,
        1: None,
        2: 0,
    }

    train_sets = {
    "J": [0,1,2],
    "Jd": [[0,1], [2]],
    "Josingle": [],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }


    prob = solve_linear_problem(train_sets, S, d_max, μ, not_considered_station)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 5
        if v.name == "Delays_2_1":
            delay = v.varValue
            assert delay == 0

    # TODO objectove should be tested to be 0.5

    ### rerouting ####
    train_sets = {
    "J": [0,1,2],
    "Jd": [],
    "Josingle": [[1,2], []],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }


    prob = solve_linear_problem(train_sets, S, d_max, μ, not_considered_station)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 1
        if v.name == "Delays_2_1":
            delay = v.varValue
            assert delay == 3

        # TODO objectove should be tested to be 0.4

test_linear_solver()