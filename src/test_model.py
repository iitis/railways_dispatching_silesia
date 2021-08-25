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

from helpers_functions import *
from input_data import *

from linear_solver import *
from make_qubo import *


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



def toy_problem_variables(train_sets, S, d_max, not_considered_station, μ = 30.):

    prob = solve_linear_problem(train_sets, S, d_max, μ, not_considered_station)

    print("d_1, t_1", return_delay_time(S, prob, 0,0))
    print("d_2, t_2", return_delay_time(S, prob, 1,0))
    print("d_3, 3_3", return_delay_time(S, prob, 2,1))

    print("d_1', t_1'", return_delay_time(S, prob, 0,1))


    print("impact to objective t_1", impact_to_objective(prob, 0,0, d_max))
    print("impact to objective t_2", impact_to_objective(prob, 1,0, d_max))
    print("impact to objective t_3", impact_to_objective(prob, 2,1, d_max))


# linear solver

if False:
    # this will be changed while rerouting
    train_sets = {
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    toy_problem_variables(train_sets, S, 10, not_considered_station)

    ### rerouting ####
    train_sets = {
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    toy_problem_variables(train_sets, S, 10, not_considered_station)


#####   QUBO implementation #########



if True:
    train_sets = {
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    p_sum = 2.5
    p_pair = 1.25
    p_pair_qubic = 1.25
    p_qubic = 2.1

    Q = make_Q(train_sets, S, not_considered_station, 10, p_sum, p_pair, p_pair_qubic, p_qubic)

    print(np.sqrt(np.size(Q)))

    np.savez("files/Qfile.npz", Q=Q)

    solution = np.load("files/solution.npz")


    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
    l = q_bits

    #print(solution[0:l-1])

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


if True:
    train_sets = {
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    Q = make_Q(train_sets, S, not_considered_station, 10, p_sum, p_pair, p_pair_qubic, p_qubic)

    np.savez("files/Qfile_r.npz", Q=Q)

    solution = np.load("files/solution_r.npz")


    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
    l = q_bits

    print(" ... rerouting ....")

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, j,s)
            print("train", j, "station", s, "delay", d, "time", t)
