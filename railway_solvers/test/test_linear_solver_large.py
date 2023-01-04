"""test ILP on larger problem """
import pytest
import importlib

from railway_solvers import (
    solve_linear_problem, delay_and_acctual_time
    )

def test_5_trains_all_cases():
    """
    We have the following trains: 21,22,23,24,25
    and stations: A,B,C,D    [  ] - corresponds to the platform
    and tracks: ----     .....

    the way trains go ->
    22 <-> 23 means that 22 ends, and then starts back as 23
    (rolling stock circ)

    the example sitation map is following:



       -21, 22, -> --------------------------21 ->-- <-24--
       [  A   ]        [ B  ]         .   .       [ C ]
       -------------------------<- 23--c ---- 22 <-> 23 ---
                                      .
          . -- 25-> - .             .
      --- .  [ D  ]   . ----<- 24---
            .........

    """

    file = "5_trains_all_cases"
    file_name = f"inputs4QUBO.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)


    prob = solve_linear_problem(train_sets, timetable, d_max)

    for v in prob.variables():
        print(v)
        print(v.varValue)

    assert delay_and_acctual_time(
        train_sets, timetable, prob, 21, "A"
    ) == (0.0, 6.0, 6.0)
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 22, "A"
    ) == (7.0, 8.0, 1.0)
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 21, "B"
    ) == (0.0, 11.0 ,11.0)
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 22, "B"
    ) == (7.0, 17.0, 10.0)
    # 17 + pass + prep = 17+8+3
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 23, "C"
    ) == (2.0, 28.0, 26.0)
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 23, "B"
    ) == (2.0, 35.0, 33.0)

    assert delay_and_acctual_time(
        train_sets, timetable, prob, 24, "C"
    ) == (1.0, 26.0, 25.0)
    # 26 + pass + switch = 26 + 3 + 1
    assert delay_and_acctual_time(
        train_sets, timetable, prob, 25, "D"
    ) == (2.0, 30.0, 28.0)
    assert prob.objective.value() == pytest.approx(1.01)


def test_many_trains_single_line():
    """
    the simple exapme with many trains between stations A and B
    trains number according to PLK rules (add one way, even another)


      --10, 12, 14, 16 --> -----------------------------------------
             [ A ]         .                  .           [ B ]
       -------------------                     --<- 11, 13, 15, 17--


    """
    file = "many_trains_single_line"
    file_name = f"inputs4QUBO.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)

    prob = solve_linear_problem(train_sets, timetable, d_max)

    for v in prob.variables():
        print(v)
        print(v.varValue)

    assert prob.objective.value() == pytest.approx(0.25)
