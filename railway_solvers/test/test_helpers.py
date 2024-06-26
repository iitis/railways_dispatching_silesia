"""test helpers functions"""

from railway_solvers import( 
    occurs_as_pair,
    update_dictofdicts,
    previous_station,
    tau,
    penalty_weights,
    earliest_dep_time,
    not_the_same_rolling_stock,
    departure_station4switches,
    get_M,
    skip_station,
    subsequent_station,
    previous_train_from_Jround,
    subsequent_train_at_Jround,
    are_two_trains_entering_via_the_same_switches,
    can_MO_on_line
    )

def test_pairs():
    """test occurs in pairs """
    assert occurs_as_pair(1, 2, [[1, 2, 3], [4], [5, 6]]) is True
    assert occurs_as_pair(2, 1, [[1, 2, 3], [4], [5, 6]]) is True
    assert occurs_as_pair(1, 4, [[1, 2, 3], [4], [5, 6]]) is False

    d1 = {0: {0: 1, 1: 2}, 1: {0: 1}}
    d2 = {0: {2: 3}}
    assert update_dictofdicts(d1, d2) == {0: {0: 1, 1: 2, 2: 3}, 1: {0: 1}}

    d1 = {0: {0: 1, 1: 2}, 1: {0: 1}}
    d2 = {2: {2: 3}}
    assert update_dictofdicts(d1, d2) == {0: {0: 1, 1: 2}, 1: {0: 1}, 2: {2: 3}}


def test_trains_paths():
    """test previous, following statiosn of trains"""
    S = {0: [0, 1, 2, 4], 1: [0, 1, 2], 2: [1, 0]}

    assert previous_station(S[0], 4) == 2
    assert previous_station(S[2], 1) is None
    assert subsequent_station(S[1], 2) is None
    assert subsequent_station(S[0], 2) == 4
    assert subsequent_station(S[2], 1) == 0


def test_auxiliary_timetable_functions():
    """test functions o timetable"""
    taus = {
        "pass":{"0_0_1": 5, "1_0_1": 7, "2_1_0": 10},
        "headway":{"0_1_0_1": 2, "1_0_0_1": 5},
        "stop": {"0_1": 1, "1_1": 2, "2_0": 1},
        "res": 3,
    }
    schedule = {"0_0": -10, "1_0": 0, "2_1": 0, "0_1": -3, "1_1": 9, "2_0": 11}
    timetable = {
        "tau": taus,
        "schedule": schedule,
        "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
        "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1},
    }

    assert tau(timetable, "pass", first_train=0, first_station=0, second_station=1) == 5
    assert tau(timetable, "res") == 3
    assert penalty_weights(timetable, 1, 0) == 1
    assert penalty_weights(timetable, 1, 1) == 0
    assert penalty_weights(timetable, 2, 1) == 1

    S = {0: [0, 1], 1: [0, 1], 2: [1, 0]}
    assert earliest_dep_time(S, timetable, 0, 0) == 4
    assert earliest_dep_time(S, timetable, 0, 1) == 10
    assert earliest_dep_time(S, timetable, 2, 0) == 19
    assert earliest_dep_time(S, timetable, 2, 1) == 8

def test_helpers_of_train_sets():
    """test helpers on the trains schedule"""

    train_sets = {
        "Paths": {1: ["A", "B"], 2: ["B", "A"], 3: ["A", "B"]},
        "Jround": {"B": [[1, 2]]},
        "Jswitch": {"B": [{1: "out", 3: "out"}, {1: "in", 3: "in"}]},
    }

    assert not_the_same_rolling_stock(0, 1, train_sets) is True
    assert not_the_same_rolling_stock(0, 1, train_sets) is True
    assert not_the_same_rolling_stock(1, 2, train_sets) is False

    assert departure_station4switches("B", 1, {1: "out", 3: "out"}, train_sets) == "B"
    assert departure_station4switches("B", 1, {1: "in", 3: "in"}, train_sets) == "A"
    assert get_M(2, 3, 4) == 5
    assert skip_station(1, "A", train_sets) is False

    assert previous_train_from_Jround(train_sets, 2, "B") == 1
    assert subsequent_train_at_Jround(train_sets, 1, "B") == 2
    assert previous_train_from_Jround(train_sets, 1, "B") is None
    assert subsequent_train_at_Jround(train_sets, 2, "B") is None

    assert are_two_trains_entering_via_the_same_switches(train_sets, "B", 1, 3) is True
    assert are_two_trains_entering_via_the_same_switches(train_sets, "B", 1, 2) is False
    assert are_two_trains_entering_via_the_same_switches(train_sets, "A", 1, 3) is False

    train_sets = {
        "Paths": {1: ["A", "B"], 2: ["C", "B"], 3: ["A", "B"]},
        "Jd": {"A":{"B":[[1,3]]}, "C":{"B":[[2]]}},
    }

    assert can_MO_on_line(1, 3, "B", train_sets) is False
    assert can_MO_on_line(1, 2, "B", train_sets) is True

    train_sets = {
        "Paths": {1: ["A", "B"], 2: ["C", "B"], 3: ["A", "B"]},
        "Jd": {"A":{"B":[[1],[3]]}, "C":{"B":[[2]]}},
    }
    assert can_MO_on_line(1, 3, "B", train_sets) is True
    assert can_MO_on_line(1, 2, "B", train_sets) is True
