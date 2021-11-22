import pytest
from railway_solvers import *

def energy(v, Q):
    if -1 in v:
        v = [(y+1)/2 for y in v]
    X = np.array(Q)
    V = np.array(v)
    return V @ X @ V.transpose()

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
                 "penalty_weights": {"21_B": 2, "22_B": 0.5, "21_A": 2, "22_A": 0.5, "23_B":0.8, "24_C":0.5, "25_D":0.5}}

    train_sets = {
        "skip_station": {
            21: None,
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
        "Jtrack": {'B': [[21, 22]], 'C':[[21,24], [22, 23]]},
        "Jswitch": {'B':[['B', 'B', 21, 22], ['A', 'A', 21, 22]], 'C': [['C', 'C', 23, 24], ['B', 'C', 22, 24], ['B', 'C', 22, 23], ['B', 'C', 21, 24]], 'D': [['C', 'D', 24, 25]]}
    }

    d_max = 10

    prob = solve_linear_problem(train_sets, timetable, d_max, 30)

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


    p_sum = 2.5
    p_pair = 1.25
    p_pair_qubic = 1.25
    p_qubic = 2.1

    Q = make_Q(train_sets, timetable, d_max, p_sum,
               p_pair, p_pair_qubic, p_qubic)

    np.savez("test/files/Qfile_5trains.npz", Q=Q)

    sol = np.load("test/files/solution_5trains.npz")

    # (2*3+1+2)*2.5

    assert energy(sol, Q) == pytest.approx(-22.5+1.01, .02)

def test_many_trains_single_line():

    "   10, 12, 14, 16 -->                             "
    "  ----------------------------------------       "
    "    [ A ]    /                  \    [ B ]         "
    "   ---------                      -----------     "
    "                                   <- 11,13,15,17 "

    taus = {"pass": {"10_A_B": 4, "12_A_B": 4, "14_A_B": 4, "16_A_B": 4, "11_B_A": 4, "13_B_A": 4, "15_B_A": 4, "17_B_A": 4},
          "blocks": {"10_12_A_B": 2, "10_14_A_B": 2, "10_16_A_B": 2, "12_14_A_B": 2, "12_16_A_B": 2, "14_16_A_B": 2,
                    "12_10_A_B": 2, "14_10_A_B": 2, "16_10_A_B": 2, "14_12_A_B": 2, "16_12_A_B": 2, "16_14_A_B": 2,
                    "11_13_B_A": 2, "11_15_B_A": 2, "11_17_B_A": 2, "13_15_B_A": 2, "13_17_B_A": 2, "15_17_B_A": 2,
                    "13_11_B_A": 2, "15_11_B_A": 2, "17_11_B_A": 2, "15_13_B_A": 2, "17_13_B_A": 2, "17_15_B_A": 2},
                 "stop": {"10_B": 1, "12_B": 1, "14_B": 1, "16_B": 1, '11_A': 1, '13_A':1, '15_A': 1, '17_A':1},
                  "res": 1}
    timetable = {"tau": taus,
                 "initial_conditions": {"10_A": 5, "12_A": 10, "14_A": 20, "16_A": 30, "11_B": 5, "13_B": 15, "15_B": 25, "17_B": 35},
                 "penalty_weights": {"10_A": 0.5, "12_A": 0.5, "14_A": 0.5, "16_A": 0.5, "11_B": 0.5, "11_B": 0.5, "13_B": 0.5, "15_B": 0.5, "17_B": 0.5}}


    train_sets = {
        "skip_station": {
            10: "B",
            12: "B",
            14: "B",
            16: "B",
            11: "A",
            13: "A",
            15: "A",
            17: "A",

        },
        "Paths": {10: ['A', 'B'], 12: ['A', 'B'], 14: ['A', 'B'], 16: ['A', 'B'], 11: ['B', 'A'], 13: ['B', 'A'], 15: ['B', 'A'], 17: ['B', 'A']},
        "J": [10,11,12,13,14,15,16,17],
        "Jd": {'A': {'B': [[10,12,14,16]]}, 'B': {'A': [[11,13,15,17]]}},
        "Josingle": {('A', 'B'): [[10,11], [10,13], [10,15], [10,17], [12,11],
        [12,13], [12,15], [12,17], [14,11], [14,13], [14,15], [14,17], [16,11], [16,13], [16,15], [16,17]]},
        "Jround": dict(),
        "Jtrack": {'A': [[10,12,14,16]], 'B':[[11,13,15,17]]},
        "Jswitch": dict()
    }

    d_max = 10

    prob = solve_linear_problem(train_sets, timetable, d_max, 100)

    for v in prob.variables():
        print(v)
        print(v.varValue)


    assert prob.objective.value() == pytest.approx(0.25)
