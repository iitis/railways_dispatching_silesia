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
import pickle as pk

from helpers_functions import *
from input_data import *

from linear_solver import *
from make_qubo import *




def toy_problem_variables(train_sets, timetable, d_max, μ = 30.):

    prob = solve_linear_problem(train_sets, timetable, d_max, μ)

    S = train_sets["Paths"]

    print("d_1, t_1", return_delay_time(S, timetable, prob, 0,0))
    print("d_2, t_2", return_delay_time(S, timetable, prob, 1,0))
    print("d_3, t_3", return_delay_time(S, timetable, prob, 2,1))

    print("d_1', t_1'", return_delay_time(S, timetable, prob, 0,1))


    print("impact to objective t_1", impact_to_objective(prob, timetable, 0,0, d_max))
    print("impact to objective t_2", impact_to_objective(prob, timetable, 1,0, d_max))
    print("impact to objective t_3", impact_to_objective(prob, timetable, 2,1, d_max))


# linear solver

if True:

    timetable = small_timetable()

    d_max = 10

    # this will be changed while rerouting
    train_sets = {
      "skip_station":{
       0: None,
       1: None,
       2: 0,
       },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    toy_problem_variables(train_sets, timetable, d_max)

    ### rerouting ####
    train_sets = {
      "skip_station":{
        0: None,
        1: None,
        2: 0,
        },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    toy_problem_variables(train_sets, timetable, d_max)

    print("   ############   Done linear solver  #########")


#####   QUBO implementation, writng Q matrix #########

def energy(v, Q):
    if -1 in v:
        v = [(y+1)/2 for y in v]
    X = np.matrix(Q)
    V = np.matrix(v)
    return V*X*V.transpose()

if False:

    timetable = small_timetable()


    train_sets = {
      "skip_station":{
        0: None,
        1: None,
        2: 0,
        },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
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


    Q = make_Q(train_sets, timetable, 10, p_sum, p_pair, p_pair_qubic, p_qubic)

    print(np.sqrt(np.size(Q)))

    np.savez("files/Qfile.npz", Q=Q)


    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    Q = make_Q(train_sets, timetable, 10, p_sum, p_pair, p_pair_qubic, p_qubic)

    np.savez("files/Qfile_r.npz", Q=Q)



if False:

    timetable = small_timetable()

    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }


    solution = np.load("files/solution.npz")

    Q = np.load("files/Qfile.npz")["Q"]

    print("ground energy", energy(solution, Q))


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits

    print("x vars", l)
    print("all var", np.size(Q[0]))

    #print(solution[0:l-1])

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    print(" ... rerouting ....")

    solution = np.load("files/solution_r.npz")

    Q = np.load("files/Qfile_r.npz")["Q"]


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits


    print("ground energy", energy(solution, Q))

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


    print("       done      Metropols Hastings  ")


if False:

    timetable = small_timetable()

    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }


    solution = np.load("files/Qfile_sol_sim-anneal.npz")["arr_0"]

    Q = np.load("files/Qfile.npz")["Q"]

    print("ground energy", energy(solution, Q))


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits



    #print(solution[0:l-1])

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    solution = np.load("files/Qfile_sol_sim-anneal_r.npz")["arr_0"]

    Q = np.load("files/Qfile_r.npz")["Q"]

    print("ground energy", energy(solution, Q))


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits

    print(" ... rerouting ....")

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


    print("    ############   done  simulated annealer ############  ")



if True:

    timetable = small_timetable()

    train_sets = {
      "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    for i in [3, 3.5, 4, 4.5]:
      file = open("files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst"+str(i),'rb')

      print("css", i)

      x = pk.load(file)

      solution = x[0][0]

      print(x[0][1])

      Q = np.load("files/Qfile.npz")["Q"]

      print("ground energy", energy(solution, Q))


      inds, q_bits = indexing4qubo(train_sets, 10)
      l = q_bits


      S = train_sets["Paths"]

      for i in range(l):
          if solution[i] == 1:
              j = inds[i]["j"]
              s = inds[i]["s"]
              d = inds[i]["d"]
              t = d + earliest_dep_time(S, timetable, j,s)
              print("train", j, "station", s, "delay", d, "time", t)

if True:

    timetable = small_timetable()

    train_sets = {
    "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    for i in [3, 3.5, 4, 4.5]:
      file = open("files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst"+str(i)+"_r",'rb')

      print("css", i)

      x = pk.load(file)

      solution = x[0][0]

      print(x[0][1])

      Q = np.load("files/Qfile_r.npz")["Q"]

      print("ground energy", energy(solution, Q))


      inds, q_bits = indexing4qubo(train_sets, 10)
      l = q_bits

      print(" ... rerouting ....")

      S = train_sets["Paths"]

      for i in range(l):
          if solution[i] == 1:
              j = inds[i]["j"]
              s = inds[i]["s"]
              d = inds[i]["d"]
              t = d + earliest_dep_time(S, timetable, j,s)
              print("train", j, "station", s, "delay", d, "time", t)


    print(" ##########   done  DW  results  ###################")


if True:

    timetable = small_timetable()


    train_sets = {
     "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }


    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal",'rb')

    x = pk.load(file)

    solution = x[0][0]

    print(x[0][1])

    Q = np.load("files/Qfile.npz")["Q"]

    print("ground energy", energy(solution, Q))


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits



    S = train_sets["Paths"]

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)

if True:

    timetable = small_timetable()

    train_sets = {
     "skip_station":{
      0: None,
      1: None,
      2: 0,
      },
      "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r",'rb')


    x = pk.load(file)

    solution = x[0][0]

    print(x[0][1])

    Q = np.load("files/Qfile_r.npz")["Q"]

    print("ground energy", energy(solution, Q))


    inds, q_bits = indexing4qubo(train_sets, 10)
    l = q_bits

    print(" ... rerouting ....")

    S = train_sets["Paths"]

    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


    print(" ######### done  Hybrid  results ############ ")
