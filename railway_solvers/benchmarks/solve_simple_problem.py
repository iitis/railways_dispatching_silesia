#!/usr/bin/env python3
from string import printable
import sys

import os
from argparse import ArgumentParser
from typing import Protocol

import numpy as np
import pulp as pus
import itertools
import pickle as pk


sys.path.append('../src')


from helpers_functions import earliest_dep_time
from linear_solver import solve_linear_problem, return_delay_time, impact_to_objective
from make_qubo import make_Q, indexing4qubo


def energy(v, Q):
    if -1 in v:
        v = [(y+1)/2 for y in v]
    X = np.matrix(Q)
    V = np.matrix(v)
    return V*X*V.transpose()

def visualise_Qubo_solution(solution, timetable, train_sets, d_max):
    inds, q_bits = indexing4qubo(train_sets, d_max)
    l = q_bits

    print("x vars", l)
    print("all var", np.size(Q[0]))

    S = train_sets["Paths"]


    for i in range(l):
        if solution[i] == 1:
            j = inds[i]["j"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            t = d + earliest_dep_time(S, timetable, j,s)
            print("train", j, "station", s, "delay", d, "time", t)


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


taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8, "2_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_None" : 1, "1_1_None" : 1}, "res": 1}
timetable = {"tau": taus,
              "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
              "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}



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

train_sets_rerouted = {
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

d_max = 10


####  liner solver ####

if True:


    toy_problem_variables(train_sets, timetable, d_max)


    toy_problem_variables(train_sets_rerouted , timetable, d_max)

    print("   ############   Done linear solver  #########")


#####   Q matrix generation #########


if False:

    p_sum = 2.5
    p_pair = 1.25
    p_pair_qubic = 1.25
    p_qubic = 2.1


    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    print(np.sqrt(np.size(Q)))

    np.savez("files/Qfile.npz", Q=Q)



    Q = make_Q(train_sets_rerouted, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    np.savez("files/Qfile_r.npz", Q=Q)



#####  D-Wave output   ######

if True:


    for i in [3, 3.5, 4, 4.5]:
      file = open("files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst"+str(i),'rb')

      print("css", i)

      x = pk.load(file)

      solution = x[0][0]

      print(x[0][1])

      Q = np.load("files/Qfile.npz")["Q"]

      print("default setting")

      print("ground energy", energy(solution, Q))

      visualise_Qubo_solution(solution, timetable, train_sets, d_max)

    print(" ##########   done  DW  results  ###################")

#####  D-Wave output  rerouted ######


if True:


    for i in [3, 3.5, 4, 4.5]:
      file = open("files/dwave_data/Qfile_samples_sol_real-anneal_numread3996_antime250_chainst"+str(i)+"_r",'rb')

      print("css", i)

      x = pk.load(file)

      solution_r = x[0][0]


      Q_r = np.load("files/Qfile_r.npz")["Q"]

      print("rerouting")

      print("ground energy", energy(solution_r, Q_r))

      visualise_Qubo_solution(solution_r, timetable, train_sets_rerouted, d_max)


    print(" ##########   done  DW  retouted results  ###################")


#####  D-Wave hybrid solver ######

if True:


    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal",'rb')

    x = pk.load(file)

    solution = x[0][0]

    print(x[0][1])

    Q = np.load("files/Qfile.npz")["Q"]

    print("default setting")

    print("ground energy", energy(solution, Q))

    visualise_Qubo_solution(solution, timetable, train_sets, d_max)



    file = open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal_r",'rb')


    x = pk.load(file)

    solution_r = x[0][0]


    Q_r = np.load("files/Qfile_r.npz")["Q"]

    print("rerouting setting")

    print("ground energy", energy(solution_r, Q_r))


    visualise_Qubo_solution(solution_r, timetable, train_sets_rerouted, d_max)


    print(" ######### done  Hybrid  results ############ ")