import pytest

from railway_solvers import *


def test_linear_varibles_creations():
    """
        A                            B
     1 ->
     0 ->  --------------------------
    """
    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A": {"B": [[0, 1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    dv = delay_varibles(train_sets, 5)

    assert str(
        dv) == "{0: {'A': Delays_0_A, 'B': Delays_0_B}, 1: {'A': Delays_1_A, 'B': Delays_1_B}}"

    y = order_variables(train_sets)

    assert str(y) == "{0: {1: {'A': y_0_1_A}}}"


def test_minimal_span_two_trains():

    """
    two trains, 0 and 1 are going one way A -> B test minimal span

        A                            B
     1 ->
     0 ->  --------------------------
    """


    taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
            "blocks": {"0_1_A_B": 2, "1_0_A_B": 6},
            "stop": {"0_B": 1, "1_B": 1}, "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A": {"B": [[0, 1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    ####   simple problem #####
    prob = solve_linear_problem(train_sets, timetable, 5)

    v = prob.variables()

    assert v[0].name == "Delays_0_A"
    assert v[0].varValue == 0
    assert v[2].name == "Delays_1_A"
    assert v[2].varValue == 4
    assert v[4].name == "y_0_1_A"
    assert v[4].varValue == 1.
    assert prob.objective.value() == 0.4

    assert return_delay_and_acctual_time(
        train_sets["Paths"], timetable, prob, 1, "A") == (4.0, 5.0)
    assert impact_to_objective(prob, timetable, 1, "A", 5) == 0.4


def test_deadlock_and_switches_two_trains():
    """
    Two trains going opposite direction on single track line
    and swithes constrain

    station - [ A ]

    swith - c

    tracks - ......



    ..........                                        .. <- 1 ..
     [ A ]     .                                    .     [ B ]
    .. 0 -> .... c ..............................  c  ..........

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


    prob = solve_linear_problem(train_sets, timetable, 10)

    v = prob.variables()
    assert v[0].name == "Delays_0_A"
    assert v[0].varValue == 0
    assert v[3].name == "Delays_1_B"
    assert v[3].varValue == 7
    assert v[4].name == "y_0_1_A_B"
    assert v[4].varValue == 1.

    assert prob.objective.value() == pytest.approx(0.35)



def test_rolling_stock_circulation():

    """
    At station B train 0 terminates and turns intro train 1 that starts there

    ....0 -> ..................................0 <-> 1.......
    [ A ]                                       [  B  ]

    """

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]},
        "Jtrack": dict(),
        "Jswitch": dict()
    }

    taus = {"pass": {"0_A_B": 4, "1_B_A": 8}, "prep": {"1_B": 2},
            "stop":{"1_A": 0, "0_B": 0}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 3, "1_B": 1},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5}}


    prob = solve_linear_problem(train_sets, timetable, 10)

    v = prob.variables()
    assert v[0].name == "Delays_0_A"
    assert v[0].varValue == 0
    assert v[3].name == "Delays_1_B"
    assert v[3].varValue == 8

    assert prob.objective.value() == pytest.approx(0.4)



def  test_station_track_and_switches_two_trains():
    """
    Test single track at station and swithes constrain, switches simplified

    station [ A ]

    swith - c

    tracks - ......

                                                   .
                                                  .
      1 ->                                       .
    ..0 -> ...................................  c  .0-> ..  1->.....
                                                         [ B ]
     [ A  ]
                                 simplifies swith condition at B

    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 4},
            "stop": {"0_B": 1, "1_B": 1}, "res": 2}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 1},
                 "penalty_weights": {"0_A": 2, "1_A": 0.5}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": dict(),
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": dict(),
        "add_swithes_at_s": ["B"]
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[2].name == "Delays_1_A"
    assert vs[4].name == "y_0_1_B"

    assert vs[0].varValue == 0
    assert vs[2].varValue == 3
    assert vs[4].varValue == 1

    assert prob.objective.value() == pytest.approx(0.3)



def  test_station_track_and_circulation():
    """
    test station trach and circulation

    station [ A ]

    swith - c

    tracks - ......

                                    < -- 1
    .............................................
                                                  .
    .. 0 -> ........................................   0  <--->  1  ...
       2 ->                                                [ B ]
     [ A  ]


    """

    taus = {"pass": {"0_A_B": 4, "1_B_A": 4, "2_A_B": 4},
            "stop": {"0_B": 0, "1_A": 1, "2_B": 1}, "res": 1,
            "blocks": {"0_2_A_B": 2, "2_0_A_B": 2},"prep": {"1_B": 5}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_B": 2, "2_A": 2},
                 "penalty_weights": {"0_A": 2, "1_B": 0.5, "2_A": 1}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"], 2: ["A", "B"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 2]]}, "B": {"A": [[1]]}},
        "Jtrack": {"B": [[0,1,2]]},
        "Jswitch": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]}
    }

    prob = solve_linear_problem(train_sets, timetable, 10)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[3].name == "Delays_1_B"
    assert vs[4].name == "Delays_2_A"
    assert vs[6].name == "y_0_2_A"
    assert vs[7].name == "y_0_2_B"
    assert vs[8].name == "y_1_2_B"

    assert vs[0].varValue == 0
    assert vs[3].varValue == 8
    assert vs[4].varValue == 4

    S = train_sets["Paths"]

    assert return_delay_and_acctual_time(S, timetable, prob, 0, "A") == (0., 1.)

    assert return_delay_and_acctual_time(S, timetable, prob, 1, "B") == (8.0, 10.0)

    assert  return_delay_and_acctual_time(S, timetable, prob, 2, "A") == (4.0, 6.0)
    assert  return_delay_and_acctual_time(S, timetable, prob, 2, "B") == (4.0, 11.0)

    assert prob.objective.value() == pytest.approx(0.8)



def  test_station_track_and_circulation2():
    """
    test station trach and circulation

    station [ A ]

    swith - c

    tracks - ......

                                    < -- 1
    .............................................
                                                  .
    .. 0 -> ........................................   0  <--->  1  ...
       2 ->                                                [ B ]
     [ A  ]


    """

    taus = {"pass": {"0_A_B": 4, "1_B_A": 4, "2_A_B": 4},
            "stop": {"0_B": 0, "1_A": 1, "2_B": 1}, "res": 1,
            "blocks": {"0_2_A_B": 2, "2_0_A_B": 2},"prep": {"1_B": 10}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 5, "1_B": 2, "2_A": 2},
                 "penalty_weights": {"0_A": .5, "1_B": .5, "2_A": 10.}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["B", "A"], 2: ["A", "B"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 2]]}, "B": {"A": [[1]]}},
        "Jtrack": {"B": [[0,1,2]]},
        "Jswitch": dict(),
        "Josingle": dict(),
        "Jround": {"B": [[0,1]]}
    }

    prob = solve_linear_problem(train_sets, timetable, 20)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[3].name == "Delays_1_B"
    assert vs[4].name == "Delays_2_A"
    assert vs[6].name == "y_0_2_A"
    #assert vs[7].name == "y_0_2_B"
    #assert vs[8].name == "y_1_2_B"
    print(vs)

    print(vs[0].varValue)
    print(vs[3].varValue)
    print(vs[4].varValue)

    print(vs[6].varValue)
    print(vs[7].varValue)


    S = train_sets["Paths"]

    assert return_delay_and_acctual_time(S, timetable, prob, 0, "A") == (0., 5.)

    assert return_delay_and_acctual_time(S, timetable, prob, 1, "B") == (17.0, 19.0)
    assert  return_delay_and_acctual_time(S, timetable, prob, 2, "A") == (0., 2.)


    #assert prob.objective.value() == pytest.approx(1.5)



def test_linear_solver_default_problem():

    """
                                            <- 2
    ...............................................
     [ A ]                             .   .  [ B ]
    .....................................c.........
    0 ->
    1 ->
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
            "blocks": {"0_1_A_B": 2, "1_0_A_B": 6},
            "stop": {"0_B": 1, "1_B": 1},
            "res": 1
            }

    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

    d_max = 10

    train_sets = {
        "skip_station": {
            2: "A",  # we do not count train 2 leaving A
        },
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": dict(),
        "add_swithes_at_s": ["B"]
    }

    #rerouting

    """
    1 ->                                       <- 2
    ...............................................
     [ A ]                             .   .  [ B ]
    .....................................c.........
    0 ->
    """


    train_sets_rerouted = {
        "skip_station": {
            2: "A",
        },
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
        "add_swithes_at_s": ["B"]
    }

    prob = solve_linear_problem(train_sets, timetable, d_max)

    v = prob.variables()

    assert v[0].name == "Delays_0_A"
    assert v[0].varValue == 0
    assert v[1].name == "Delays_0_B"
    assert v[1].varValue == 0
    assert v[2].name == "Delays_1_A"
    assert v[2].varValue == 5
    assert v[4].name == "Delays_2_B"
    assert v[4].varValue == 0

    assert prob.objective.value() == 0.5

    prob = solve_linear_problem(train_sets_rerouted, timetable, d_max)

    v = prob.variables()

    assert v[0].name == "Delays_0_A"
    assert v[0].varValue == 0
    assert v[1].name == "Delays_0_B"
    assert v[1].varValue == 0
    assert v[2].name == "Delays_1_A"
    assert v[2].varValue == 1
    assert v[4].name == "Delays_2_B"
    assert v[4].varValue == 3


    assert prob.objective.value() == 0.4


def test_constraint_labels():
    """
                                            <- 2
    ...............................................
     [ A ]                             .   .  [ B ]
    .....................................c.........
    0 ->
    1 ->
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
            "blocks": {"0_1_A_B": 2, "1_0_A_B": 6},
            "stop": {"0_B": 1, "1_B": 1},
            "res": 1
            }

    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
                 "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

    d_max = 10

    train_sets = {
        "skip_station": {
            2: "A",
        },
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": dict(),
        "add_swithes_at_s": ["B"]
    }

    #rerouting

    """
    1 ->                                       <- 2
    ...............................................
     [ A ]                             .   .    [ B ]
    .....................................c.........
    0 ->
    """


    train_sets_rerouted = {
        "skip_station": {
            2: "A",
        },
        "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
        "J": [0, 1, 2],
        "Jd": dict(),
        "Josingle": {("A", "B"): [[1,2]]},
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
        "add_swithes_at_s": ["B"]
    }

    prob = create_linear_problem(train_sets, timetable, d_max)
    cnames = [cname for cname, _ in prob.constraints.items()]
    from re import match
    assert all(not match("_C[0-9]+", c) for c in cnames)

    prob = create_linear_problem(train_sets_rerouted, timetable, d_max)
    cnames = [cname for cname, _ in prob.constraints.items()]
    from re import match
    assert all(not match("_C[0-9]+", c) for c in cnames)
