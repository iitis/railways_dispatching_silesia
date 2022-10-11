import pytest

from railway_solvers import delay_varibles, order_variables, solve_linear_problem
from railway_solvers import create_linear_problem, delay_and_acctual_time
from railway_solvers import  impact_to_objective

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

    assert str(y) == "{0: {1: {'one_station': {'A': y_0_1_one_station_A}}}}"


def test_minimal_span_two_trains():

    """
    two trains, 0 and 1 are going one way A -> B test minimal span

        A                            B
     1 ->
     0 ->  --------------------------
    """


    taus = {"pass": {"0_A_B": 4, "1_A_B": 8},
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
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
    assert v[4].name == "y_0_1_one_station_A"
    assert v[4].varValue == 1.
    assert prob.objective.value() == 0.4

    assert delay_and_acctual_time(
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
    assert v[4].name == "z_0_1_A_B"
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
    assert v[2].name == "Delays_1_B"
    assert v[2].varValue == 8

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
    assert vs[4].name == "y_0_1_one_station_B"

    assert vs[0].varValue == 0
    assert vs[2].varValue == 3
    assert vs[4].varValue == 1

    assert prob.objective.value() == pytest.approx(0.3)



def  test_M_P_with_switches_two_trains():
    """
    Test single track at station and swithes constrain, switches simplified

    station [ A ]

    swith - c

    tracks - ......

                                                                                                     .
                         .............................
                        .                              .
    1 -> .. 0 -> ....  c ..............................  c  . 1 -> .. 0 -> ....

            [ A  ]                                               [ B ]



    """

    taus = {"pass": {"0_A_B": 6, "1_A_B": 2},
            "stop": {"0_B": 1, "1_B": 1}, "res": 2}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 5},
                 "penalty_weights": {"0_B": 1., "1_B": 2.}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A":{"B": [[0], [1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"A": [[0, 1]], "B": [[0, 1]]},
        "Jswitch": {"A": [{0:"out", 1:"out"}], "B": [{0:"in", 1:"in"}]}
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[1].name == "Delays_0_B"
    assert vs[2].name == "Delays_1_A"
    assert vs[3].name == "Delays_1_B"

    assert vs[4].name == "y_0_1_one_station_A"
    assert vs[5].name == "y_0_1_one_station_B"
    assert vs[6].name =="z_in_0_1_B"

    assert vs[0].varValue == 2
    assert vs[1].varValue == 2
    assert vs[2].varValue == 0
    assert vs[3].varValue == 0

    assert vs[4].varValue == 1
    assert vs[5].varValue == 0
    assert vs[6].varValue == 0

    assert prob.objective.value() == pytest.approx(0.4)



def  test_M_P_with_switches_two_trains_no_station():
    """
    Test single track at station and swithes constrain, switches simplified

    station [ A ]

    swith - c

    tracks - ......

                                                                                                     .
                         .............................
                        .                              .
    1 -> .. 0 -> ....  c ..............................  c  . 1 -> . ......
                                                           .
                                                             . ... 0 -> ...
            [ A  ]                                               [ B ]



    """

    taus = {"pass": {"0_A_B": 6, "1_A_B": 2},
            "stop": {"0_B": 1, "1_B": 1}, "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 5},
                 "penalty_weights": {"0_B": 1., "1_B": 2.}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["A", "B"]},
        "J": [0, 1],
        "Jd": {"A":{"B": [[0], [1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"A": [[0, 1]]},
        "Jswitch": {"A": [{0:"out", 1:"out"}], "B": [{0:"in", 1:"in"}]}
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[1].name == "Delays_0_B"
    assert vs[2].name == "Delays_1_A"
    assert vs[3].name == "Delays_1_B"

    assert vs[4].name == "y_0_1_one_station_A"
    assert vs[5].name =="z_in_0_1_B"


    assert vs[0].varValue == 1
    assert vs[1].varValue == 1
    assert vs[2].varValue == 0
    assert vs[3].varValue == 0

    assert vs[4].varValue == 1
    assert vs[5].varValue == 0


    assert prob.objective.value() == pytest.approx(0.2)



def  test_swithes_three_trains():
    """
    Test single track at station and swithes constrain, switches simplified

    station [ A ]

    swith - c

.
                1 ->  .........   .
                        [ C ]       .
                                       .
                                         .
     0 -> .... .........................  c  . 1 -> .. 0 -> ....

            [ A  ]                                     [ B ]



    """

    taus = {"pass": {"0_A_B": 4, "1_C_B": 4},
            "stop": {"0_B": 1, "1_B": 1}, "res": 2}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_C": 1},
                 "penalty_weights": {"0_B": 1., "1_B": 2.}}

    train_sets = {
        "Paths": {0: ["A", "B"], 1: ["C", "B"]},
        "J": [0, 1],
        "Jd": {"A":{"B": [[0]]}, "C":{"B": [[1]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {"B": [[0, 1]]},
        "Jswitch": {"B": [{0:"in", 1:"in"}]}
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()

    assert vs[0].name == "Delays_0_A"
    assert vs[1].name == "Delays_0_B"
    assert vs[2].name == "Delays_1_B"
    assert vs[3].name == "Delays_1_C"

    assert vs[4].name == "y_0_1_one_station_B"
    assert vs[5].name =="z_in_0_1_B"

    assert vs[0].varValue == 2
    assert vs[1].varValue == 2
    assert vs[2].varValue == 0
    assert vs[3].varValue == 0

    assert vs[4].varValue == 0
    assert vs[5].varValue == 0


    assert prob.objective.value() == pytest.approx(0.4)


def  test_station_track_and_circulation():

    """
    test station track and circulation

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
            "headway": {"0_2_A_B": 2, "2_0_A_B": 2},"prep": {"1_B": 5}}
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


    assert vs[5].name == "y_0_2_one_station_A"
    assert vs[6].name == "y_0_2_one_station_B"
    assert vs[7].name == "y_1_2_one_station_B"

    assert vs[5].varValue == 1.
    assert vs[6].varValue == 1.
    assert vs[7].varValue == 1.

    S = train_sets["Paths"]

    assert delay_and_acctual_time(S, timetable, prob, 0, "A") == (0., 1.)

    assert delay_and_acctual_time(S, timetable, prob, 1, "B") == (8.0, 10.0)

    assert  delay_and_acctual_time(S, timetable, prob, 2, "A") == (4.0, 6.0)
    assert  delay_and_acctual_time(S, timetable, prob, 2, "B") == (4.0, 11.0)

    assert prob.objective.value() == pytest.approx(0.8)



def  test_station_track_and_circulation2():
    """
    test station track and circulation

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
            "headway": {"0_2_A_B": 2, "2_0_A_B": 2},"prep": {"1_B": 10}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_B": 2, "2_A": 2},
                 "penalty_weights": {"0_A": 1., "1_B": 1., "2_A": 1.}}

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


    assert vs[5].name == "y_0_2_one_station_A"
    assert vs[6].name == "y_0_2_one_station_B"
    assert vs[7].name == "y_1_2_one_station_B"
    assert vs[5].varValue == 0.
    assert vs[6].varValue == 0.
    assert vs[7].varValue == 0.



    S = train_sets["Paths"]


    assert delay_and_acctual_time(S, timetable, prob, 0, "A") == (3., 4.)

    assert delay_and_acctual_time(S, timetable, prob, 1, "B") == (16.0, 18.0)
    assert delay_and_acctual_time(S, timetable, prob, 2, "A") == (0., 2.)


    assert prob.objective.value() == pytest.approx(0.95)

def  test_station_followed_by_station_KO_STMcase():
    """
    test station track and circulation

    station [ A ]

    swith - c

    tracks - ......

   .........                                 .......
    .. 0 -> ........................................
       1 ->
     [ A  ]   [ B ]                           [ C  ]


    """

    taus = {"pass": {"0_A_B": 0, "1_A_B": 0, "0_B_C": 4, "1_B_C": 4},
            "stop": {"0_B": 3, "1_B": 1, "0_C": 1, "1_C": 1},
            "headway": {"0_1_B_C": 2, "1_0_B_C": 2, "0_1_A_B": 0, "1_0_A_B": 0}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_A": 1, "1_A": 2},
                 "penalty_weights": {"0_C": 2., "1_C": 1.}}

    train_sets = {
        "Paths": {0: ["A", "B", "C"], 1: ["A", "B", "C"]},
        "J": [0, 1],
        "Jd": {"A": {"B": [[0, 1]]}, "B": {"C": [[0, 1]]}},
        "Jtrack": {"B": [[0,1]]},
        "Jswitch": dict(),
        "Josingle": dict(),
        "Jround": dict()
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()


    S = train_sets["Paths"]


    assert delay_and_acctual_time(S, timetable, prob, 0, "A") == (0., 1.)
    assert delay_and_acctual_time(S, timetable, prob, 0, "B") == (0., 4.)
    assert delay_and_acctual_time(S, timetable, prob, 0, "C") == (0., 9.)

    assert delay_and_acctual_time(S, timetable, prob, 1, "A") == (2., 4.)
    assert delay_and_acctual_time(S, timetable, prob, 1, "B") == (3., 6.)
    assert delay_and_acctual_time(S, timetable, prob, 1, "C") == (3., 11.)

    assert prob.objective.value() == pytest.approx(0.6)

def  test_3stationsIC_STM_KO_case():
    """
    test station track and circulation

    station [ A ]

    swith - c

    tracks - ......

    ......
    .. 0 -> ...............
       1 ->
     [ KO(IC)]  [ KO(STM) ]  [ KO  ]


    """

    taus = {"pass": {"0_KO(IC)_KO(STM)": 0, "1_KO(IC)_KO(STM)": 0,
                    "0_KO(STM)_KO": 0, "1_KO(STM)_KO": 0},
            "stop": {"0_KO(STM)": 3, "1_KO(STM)": 1, "0_KO": 1, "1_KO": 1},
            "headway": {"0_1_KO(STM)_KO": 0, "1_0_KO(STM)_KO": 0,
                        "0_1_KO(IC)_KO(STM)": 0, "1_0_KO(IC)_KO(STM)": 0}}
    timetable = {"tau": taus,
                 "initial_conditions": {"0_KO(IC)": 1, "1_KO(IC)": 2},
                 "penalty_weights": {"0_KO": 2., "1_KO": 1.}}

    train_sets = {
        "Paths": {0: ["KO(IC)", "KO(STM)", "KO"], 1: ["KO(IC)", "KO(STM)", "KO"]},
        "J": [0, 1],
        "Jd": {"KO(IC)": {"KO(STM)": [[0, 1]]}, "KO(STM)": {"KO": [[0, 1]]}},
        "Jtrack": {"KO(STM)": [[0,1]], "KO": [[0,1]]},
        "Jswitch": dict(),
        "Josingle": dict(),
        "Jround": dict()
    }

    prob = solve_linear_problem(train_sets, timetable, 5)

    vs = prob.variables()


    S = train_sets["Paths"]


    assert delay_and_acctual_time(S, timetable, prob, 0, "KO(IC)") == (0., 1.)
    assert delay_and_acctual_time(S, timetable, prob, 0, "KO(STM)") == (0., 4.)
    assert delay_and_acctual_time(S, timetable, prob, 0, "KO") == (0., 5.)

    assert delay_and_acctual_time(S, timetable, prob, 1, "KO(IC)") == (2., 4.)
    assert delay_and_acctual_time(S, timetable, prob, 1, "KO(STM)") == (2., 5.)
    assert delay_and_acctual_time(S, timetable, prob, 1, "KO") == (2., 6.)

    assert prob.objective.value() == pytest.approx(0.4)




def test_HOBO_problems():

    """
                                            <- 2
    ...............................................
     [ A ]                             .   .  [ B ]
    .....................................c.........
    0 ->
    1 ->
    """

    taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
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

    S = train_sets["Paths"]

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


    assert delay_and_acctual_time(S, timetable, prob, 0, "A") == (0,4)
    assert delay_and_acctual_time(S, timetable, prob, 1, "A") == (5,6)
    assert delay_and_acctual_time(S, timetable, prob, 2, "B") == (0, 8)
    assert delay_and_acctual_time(S, timetable, prob, 0, "B") == (0, 9)


    assert impact_to_objective(prob, timetable, 0, "A", d_max) == pytest.approx(0)
    assert impact_to_objective(prob, timetable, 1, "A", d_max) == pytest.approx(0.5)
    assert impact_to_objective(prob, timetable, 2, "B", d_max) == pytest.approx(0)

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

    S = train_sets_rerouted["Paths"]

    assert delay_and_acctual_time(S, timetable, prob, 0, "A") == (0,4)
    assert delay_and_acctual_time(S, timetable, prob, 1, "A") == (1,2)
    assert delay_and_acctual_time(S, timetable, prob, 2, "B") == (3, 11)
    assert delay_and_acctual_time(S, timetable, prob, 0, "B") == (0, 9)


    assert impact_to_objective(prob, timetable, 0, "A", d_max) == pytest.approx(0)
    assert impact_to_objective(prob, timetable, 1, "A", d_max) == pytest.approx(0.1)
    assert impact_to_objective(prob, timetable, 2, "B", d_max) == pytest.approx(0.3)

    """

                                        <- j3  j4
    ..........c........................c....c......
     [ S1 ] .  .                        .  .   [ S2 ]
    .......c....c........................c.........
    j1 ->
    j2 ->



    S1, S2 - stations
    j1, j2, j3 - trains
    .....  - track
    c - switch
    """

    taus = {"pass": {"j1_S1_S2": 4, "j2_S1_S2": 8, "j3_S2_S1": 8, "j4_S2_S1": 8},
                     "headway": {"j1_j2_S1_S2": 2, "j2_j1_S1_S2": 6, "j3_j4_S2_S1": 2, "j4_j3_S2_S1": 2},
                     "stop": {"j1_S2": 1, "j2_S2": 1},
                     "res": 1
                    }


    trains_timing = {"tau": taus,
                     "initial_conditions": {"j1_S1": 4, "j2_S1": 1, "j3_S2": 8, "j4_S2": 9},
                     "penalty_weights": {"j1_S1": 2, "j2_S1": 1, "j3_S2": 1, "j4_S2": 1}
                     }

    trains_paths_enlarged = {
            "skip_station": {
                "j3": "S1",  "j4": "S1",  # we do not count train j3 leaving S1
            },
            "Paths": {"j1": ["S1", "S2"], "j2": ["S1", "S2"], "j3": ["S2", "S1"], "j4": ["S2", "S1"]},
            "J": ["j1", "j2", "j3", "j4"],
            "Jd": {"S1": {"S2": [["j1", "j2"]]}, "S2": {"S1": [["j3", "j4"]]}},
            "Josingle": {},
            "Jround": {},
            "Jtrack": {"S2": [["j1", "j2"]]},
            "Jswitch": {},
            "add_swithes_at_s": ["S2"]  # additional τ(res.)(j, "B") in Eq. 18
            }

    prob = solve_linear_problem(trains_paths_enlarged, trains_timing , d_max)

    assert prob.objective.value() == 0.6

    v = prob.variables()

    assert v[0].name == "Delays_j1_S1"
    assert v[0].varValue == 0
    assert v[1].name == "Delays_j1_S2"
    assert v[1].varValue == 0
    assert v[2].name == "Delays_j2_S1"
    assert v[2].varValue == 5
    assert v[4].name == "Delays_j3_S2"
    assert v[4].varValue == 0
    assert v[5].name == "Delays_j4_S2"
    assert v[5].varValue == 1




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
            "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
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
