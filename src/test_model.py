#!/usr/bin/env python3
from string import printable
import sys
import os
from argparse import ArgumentParser
from typing import Protocol
# import datetime as dt
# from copy import deepcopy
import numpy as np
import pulp as pus
import itertools

# sys.path.append(os.path.abspath("./QUBO"))

#unavoidable delay on train 1 tU(j1, s1out), train 2 tU(j2, s1out), and train 3 tU(j3, s2out) (on station 2).

# model input

# proposed renumbering trains j_1 -> 0, j_2 -> 1, j_3 -> 2; stations s_1 -> 0, s_2 -> 1

#######  these are input ##########

def tau(x = None, train = None, first_station = None, second_station = None):
    #print(x, train, first_station, second_station)
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


def initial_conditions(train = None, station = None):
    t = -1
    if train == 0 and station == 0:
        t = 4
    elif train == 1 and station == 0:
        t = 1
    elif train == 2 and station == 1:
        t = 8
    return t


def penalty_weights(train = None, station = None):
    w = 0.
    if train == 0 and station == 0:
        w = 2.
    elif train == 1 and station == 0:
        w = 1.
    elif train == 2 and station == 1:
        w = 1.
    return w


S = {
    0: [0,1],
    1: [0,1],
    2: [1,0]
}

### this two cona be changed during rerouting

train_sets = {
  "J": [0,1,2],
  "Jd": [[0,1], [2]],
  "Josingle": [],
  "Jround": dict(),
  "Jtrack": dict(),
  "Jswitch": dict()
}


not_considered_stations = {
    0: None,
    1: None,
    2: 0
}


def subsequent_station(S, j, s):
    path = S[j]
    k = path.index(s)
    if k == len(path)-1:
        return None
    else:
        return path[k+1]

def previous_station(S, j, s):
    path = S[j]

    k = path.index(s)

    if k == 0:
        return None
    else:
        return path[k-1]


def earliest_dep_time(train = None, station = None):

    t = initial_conditions(train, station)
    if t >= 0:
        return t
    else:
        s = previous_station(S, train, station)
        return earliest_dep_time(train, s) + tau('pass', train, s, station) + tau('stop', train, station)


def common_path(S, j, jp):
    return [s for s in S[j] if s in S[jp]]


def minimal_span(problem, delay_var, y, S, train_sets, μ):
    "minimum span condition"
    for js in train_sets["Jd"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp):

                s_next = subsequent_station(S, j, s)
                s_nextp = subsequent_station(S, jp, s)

                if (s_next != None and s_next == s_nextp):

                    problem += delay_var[jp][s] + earliest_dep_time(jp, s) + μ*(1-y[j][jp][s]) - delay_var[j][s] - earliest_dep_time(j, s) \
                     >= tau('blocks', j, s, s_next) + max(0, tau('pass', j, s, s_next) - tau('pass', jp, s, s_next))

                    problem += delay_var[j][s] + earliest_dep_time(j, s) + μ*y[j][jp][s] - delay_var[jp][s] - earliest_dep_time(jp, s) \
                    >= tau('blocks', jp, s, s_next) + max(0, tau('pass', jp, s, s_next) - tau('pass', j, s, s_next))



def minimal_stay(problem, delay_var, S, train_sets):
    "minimum stay condition"
    for j in train_sets["J"]:
        for s in S[j]:

            s_previous = previous_station(S, j, s)

            if (s_previous != None and s != not_considered_stations[j]):
                problem += delay_var[j][s]  >= delay_var[j][s_previous]


def objective(problem, delay_var, S, train_sets, d_max):
    "objective function"
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(i, j)/d_max for i in train_sets["J"] for j in S[0] if penalty_weights(i,j) !=0])


def toy_problem_variables(trains_inds, no_station, d_max):

    μ = 30.
    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var = pus.LpVariable.dicts("Delays", (trains_inds, no_station), 0, d_max, cat='Integer')
    
    for key, value in secondary_delays_var.items():

        if not_considered_stations[key] != None:
            v = not_considered_stations[key]


    order_the_same_dir = dict()

    for js in train_sets["Jd"]:
        train1 = []
        train2 = []
        no_station = []
        for pair in itertools.combinations(js, 2):
            train1.append(pair[0])
            train2.append(pair[1])

            no_station = common_path(S, pair[0], pair[1])
            if len(js) > 1:

                order_the_same_dir.update(pus.LpVariable.dicts("y", (train1, train2, no_station), 0, 1, cat='Integer'))

    minimal_span(prob, secondary_delays_var, order_the_same_dir, S, train_sets, μ)
    minimal_stay(prob, secondary_delays_var, S, train_sets)
    objective(prob, secondary_delays_var, S, train_sets, d_max)
    print(prob)



toy_problem_variables([0, 1, 2],[0,1], 10)