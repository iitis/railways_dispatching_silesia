import pytest
from railway_solvers import *



def test_5_trains_all_cases():

    "                                           <- 24    "
    "                                         ......     "
    "    21, 22, ->                          /  21 ->    "
    "   -----------------------------------------        "
    "   [  A   ]           [ B  ]      \ /  [ C ] 22 <-> 23 "
    "   -----------------------------------------         "
    "                           <-- 23 /                  "
    "        / -- 25-> -\             /                   "
    "   -----  [ D  ]   /------------                     "
    "        \ ------ /         <-- 24                    "



    taus = {"pass": {"21_A_B": 4, "22_A_B": 8, "21_B_C": 4, "22_B_C": 8, '23_C_B':6, '23_B_A':6, '24_C_D':3, '25_D_C':3},
                "blocks": {"21_22_A_B": 2, "22_21_A_B": 6, "21_22_B_C": 2, "22_21_B_C": 6},
                 "stop": {"21_B": 1, "22_B": 1, "21_C": 1, "22_C": 1, '23_B': 1, '23_A':1},
                 "prep": {"23_C": 3}, "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"21_A": 6, "22_A": 1, "23_C": 26, "24_C": 25, "25_D": 28},
                 "penalty_weights": {"21_B": 2, "22_B": 0.5, "21_A": 2, "22_A": 0.5, "23_B":0.8, "23_A":0.8, "24_C":0.5, "25_D":0.5}}

    train_sets = {
        "skip_station": {
            21: "C",
            22: "C",
            23: "A",
            24: "D",
            25: "C"
        },
        "Paths": {21: ['A', 'B', 'C'], 22: ['A', 'B', 'C'], 23: ['C', 'B', 'A'], 24: ['C', 'D'], 25: ['D', 'C']},
        "J": [21, 22, 23, 24, 25],
        "Jd": {'A': {'B': [[21, 22]]}, 'B': {'C': [[21, 22]]}},
        "Josingle": {('C', 'D'): [[24, 25]]},
        "Jround": {'C': [[22, 23]]},
        "Jtrack": {'B': [[21, 22]], 'C':[[21,24]]},
        "Jswitch": {'C': [['C', 'C', 23, 24], ['B', 'C', 22, 24]], 'D': [['C', 'D', 24, 25]]}
    }

    ####   simple problem #####

    prob = solve_linear_problem(train_sets, timetable, 10, 30)

    for v in prob.variables():
        print(v)
        print(v.varValue)

    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 21, 'A') == (0., 6.0)
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 22, 'A') == (7.0, 8.0)
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 21, 'B') == (0., 11.0)
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 22, 'B') == (7.0, 17.0)
    #17 + pass + prep = 17+8+3
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 23, 'C') == (2., 28.)
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 23, 'B') == (2., 35.)

    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 24, 'C') == (1., 26.)
    # 26 + pass + switch = 26 + 3 + 1
    assert return_delay_and_acctual_time(train_sets["Paths"], timetable, prob, 25, 'D') == (2., 30.)
    assert prob.objective.value() == pytest.approx(1.01)
