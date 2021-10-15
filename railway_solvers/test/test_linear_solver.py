import pytest

from railway_solvers import *


def test_linear_varibles_creations():
    train_sets = {
        "skip_station": {
            0: None,
            1: None,
        },
        "Paths": {0: [0, 1], 1: [0, 1]},
        "J": [0, 1],
        "Jd": [[0, 1]],
        "Josingle": [[]],
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    v = linear_varibles(train_sets, 5)

    assert str(
        v[0]) == "{0: {0: Delays_0_0, 1: Delays_0_1}, 1: {0: Delays_1_0, 1: Delays_1_1}}"

    assert str(v[1]) == "{0: {1: {0: y_0_1_0}}}"


def test_two_trains_going_one_way_simplest():
    taus = {"pass": {"0_0_1": 4, "1_0_1": 8}, "blocks": {"0_0_1": 2,
                                                         "1_0_1": 2}, "stop": {"0_1_None": 1, "1_1_None": 1}, "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_0": 3, "1_0": 1},
                 "penalty_weights": {"0_0": 2, "1_0": 0.5}}

    train_sets = {
        "skip_station": {
            0: None,
            1: None,
        },
        "Paths": {0: [0, 1], 1: [0, 1]},
        "J": [0, 1],
        "Jd": [[0, 1]],
        "Josingle": [[]],
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    ####   simple problem #####
    prob = solve_linear_problem(train_sets, timetable, 5, 30)

    for v in prob.variables():

        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 4
        if v.name == "y_0_1_0":
            assert v.varValue == 1.

    assert prob.objective.value() == 0.4

    assert return_delay_and_acctual_time(
        train_sets["Paths"], timetable, prob, 1, 0) == (4.0, 5.0)
    assert impact_to_objective(prob, timetable, 1, 0, 5) == 0.4


def test_two_trains_going_opposite_ways_simplest():
    train_sets = {
        "skip_station": {
            0: None,
            1: None,
        },
        "Paths": {0: [0, 1], 1: [1, 0]},
        "J": [0, 1],
        "Jd": [[]],
        "Josingle": [[0, 1]],
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    taus = {"pass": {"0_0_1": 4, "1_1_0": 8}, "blocks": {"0_0_1": 2,
                                                         "1_1_0": 2}, "stop": {"0_1_None": 1, "1_0_None": 1}, "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_0": 3, "1_1": 1},
                 "penalty_weights": {"0_0": 2, "1_1": 0.5}}

    ####   simple problem #####

    prob = solve_linear_problem(train_sets, timetable, 10, 30)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_1":
            delay = v.varValue
            assert delay == 7
        if v.name == "y_0_1_0":
            delay = v.varValue
            assert delay == 1.

    assert prob.objective.value() == pytest.approx(0.35)


def test_track_occupation_simplest():
    taus = {"pass": {"0_0_1": 4, "1_0_1": 4}, "blocks": {"0_0_1": 2,
                                                         "1_0_1": 2}, "stop": {"0_1_None": 1, "1_1_None": 1}, "res": 2}
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
        "Jd": [[]],
        "Josingle": [[]],
        "Jround": dict(),
        "Jtrack": {1: [0, 1]},
        "Jswitch": dict()
    }

    ####   simple problem #####

    prob = solve_linear_problem(train_sets, timetable, 5, 30)

    for v in prob.variables():
        if v.name == "Delays_0_0":
            delay = v.varValue
            assert delay == 0
        if v.name == "Delays_1_0":
            delay = v.varValue
            assert delay == 3
        if v.name == "y_0_1_0":
            assert v.varValue == 1.

    assert prob.objective.value() == pytest.approx(0.3)


def test_linear_solver_default_problem():
    taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {
        "0_0_1": 2, "1_0_1": 2}, "stop": {"0_1_None": 1, "1_1_None": 1}, "res": 1}
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
        "Jtrack": {1: [0, 1]},
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
        "Jtrack": {1: [0, 1]},
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

@pytest.mark.skip(reason="Note satisfied one, wait for Ozlem to finish")
def test_constraint_labels():
    taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {
        "0_0_1": 2, "1_0_1": 2}, "stop": {"0_1_None": 1, "1_1_None": 1}, "res": 1}
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
        "Jtrack": {1: [0, 1]},
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
        "Jtrack": {1: [0, 1]},
        "Jswitch": dict()
    }

    prob = create_linear_problem(train_sets, timetable, d_max, μ)
    cnames = [cname for cname, _ in prob.constraints.items()]
    from re import match
    assert all(not match("_C[0-9]+", c) for c in cnames)

    prob = create_linear_problem(train_sets_rerouted, timetable, d_max, μ)
    cnames = [cname for cname, _ in prob.constraints.items()]
    from re import match
    assert all(not match("_C[0-9]+", c) for c in cnames)
        
