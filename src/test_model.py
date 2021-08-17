#!/usr/bin/env python3
import sys
import os
from argparse import ArgumentParser
# import datetime as dt
# from copy import deepcopy
import numpy as np
import pulp as pus
import itertools

# sys.path.append(os.path.abspath("./QUBO"))

#unavoidable delay on train 1 tU(j1, s1out), train 2 tU(j2, s1out), and train 3 tU(j3, s2out) (on station 2).

# model input

# proposed renumbering trains j_1 -> 0, j_2 -> 1, j_3 -> 2; stations s_1 -> 0, s_2 -> 1

def tau(x = None, train = None, first_station = None, second_station = None):
    print(x, train, first_station, second_station)
    t = -1
    if x == 'pass' and train == 0 and first_station == 0 and second_station == 1:
        t = 4
    elif x == 'pass' and train == 1 and first_station == 0 and second_station == 1:
        t = 8
    elif x == 'pass' and train == 2 and first_station == 1 and second_station == 0:
        t = 8
    elif x == 'blocks' and train == 0 and first_station == 0 and second_station == 1:
        t = 2
    elif x == 'blocks' and train == 1 and first_station == 0 and second_station == 1:
        t = 2
    elif x == 'stop' and train == 0 and first_station == 0:
        t = 1
    elif x == 'stop' and train == 1 and first_station == 1:
        t = 1
    elif x == 'res':
        t = 1
    return t


def earliest_dep_time(train = None, station = None):
    print(train, station)
    t = -1
    if train == 0 and station == 0:
        t = 4
    elif train == 1 and station == 0:
        t = 1
    elif train == 2 and station == 1:
        t = 8
    return t

def penalty_weights(train = None, station = None):
    print(train, station)
    w = 0.
    if train == 0 and station == 0:
        w = 2.
    elif train == 1 and station == 0:
        w = 1.
    elif train == 2 and station == 1:
        w = 1.
    return w


train_sets = {
  "J": [0,1,2],
  "Jd": [[0,1], [2]],
  "Josingle": [],
  "Jround": dict(),
  "Jtrack": dict(),
  "Jswitch": dict()
}

S = {
    0: [0,1],
    1: [0,1],
    2: [1,0]
}

not_considered_stations = {
    0: None,
    1: None,
    2: 0
}


def common_path(S, j, jp):

    Sjjp = [s for s in S[j] if s in S[jp]]
    # without the last element
    return Sjjp

# print(tau('pass', 1, 1, 2))

# print(train_sets["Jswitch"])

# print(not_considered_stations[3])


def toy_problem_variables(trains_inds, no_station, d_max):

    prob = pus.LpProblem("Trains", pus.LpMinimize)


    secondary_delays_var = pus.LpVariable.dicts("Delays", (trains_inds, no_station), 0, d_max, cat='Integer')


    for key, value in secondary_delays_var.items():

        if not_considered_stations[key] != None:
            v = not_considered_stations[key]

            del value[v]

    print(secondary_delays_var)

    train1 = []
    train2 = []
    no_station = []
    order_the_same_dir = dict()

    # this will be the order variable
    for js in train_sets["Jd"]:
        for pair in itertools.combinations(js, 2):

            train1.append(pair[0])
            train2.append(pair[1])
            no_station = common_path(S, pair[0], pair[1])

    order_the_same_dir = pus.LpVariable.dicts("y", (train1, train2, no_station), 0, 1, cat='Integer')


    print(order_the_same_dir)


    # for j1 in trains_inds:
    #     for j2 in trains_inds:
    #         if VS[j1]["direction"] == VS[j2]["direction"] and j1 != j2:
    #             for k in range(np.size(no_station)):
    #                 prob += order_the_same_dir[j1][j2][k] + \
    #                         order_the_same_dir[j2][j1][k] == 1

    # for j1 in trains_inds:
    #     for j2 in trains_inds:
    #         for k in range(np.size(no_station)):
    #             prob += min_span_delay[j1][j2[k] + mu*

    print(prob)

    # minimum_span_var = pus.LpVariables.dict("Min_Span", ())


toy_problem_variables([0, 1, 2],[0,1], 10)

# def minimum_span_condition():
#     # offset = []
#     tau_ms1 = tau('blocks', 1, 1, 2)
#     con1 = max(0, tau('pass', 1, 1, 2) - tau('pass', 2, 1, 2))
#     tau_ms2 = tau('blocks', 2, 1, 2)
#     con2 = max(0, tau('pass', 2, 1, 2) - tau('pass', 1, 1, 2))
#     return tau_ms1+con1, tau_ms2+con2

# print(minimum_span_condition())


# for j1 in [1,2,3]:
    # for j2 in [1,2,3]:
        # if j1 != j2:
            # print(j1,j2)
# for s1 in [1,2]:
#         for s2 in [1,2]:
#             if s1 != s2:
#                 print(s1,s2)
