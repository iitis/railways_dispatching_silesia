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
    elif x == 'stop' and train == 0 and first_station == 1:
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

### this only will be changed during rerouting

train_sets = {
  "J": [0,1,2],
  "Jd": [[0,1], [2]],
  "Josingle": [],
  "Jround": dict(),
  "Jtrack": {1: [0,1]},
  "Jswitch": dict()
}


not_considered_station = {
    0: None,
    1: None,
    2: 0,
}

#####   functions ####


def occurs_as_pair(a,b, vecofvec):
    for v in vecofvec:
        if (a in v and b in v):
            return True
    return False



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

def update_dictofdicts(d1, d2):
    k1 = d1.keys()
    k2 = d2.keys()
    for k in k2:
        if k in k1:
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1



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


def single_line(problem, delay_var, y, S, train_sets, μ):
    "minimum span condition"
    for js in train_sets["Josingle"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp)[0:-1]:

                s_previous = previous_station(S, j, s)
                s_previousp = previous_station(S, jp, s)

                if s_previousp != None:

                    problem += delay_var[j][s] + earliest_dep_time(j, s) + μ*(1-y[j][jp][s])  \
                     >= delay_var[jp][s_previousp] + earliest_dep_time(jp, s_previousp) + tau('pass', jp, s_previousp , s)

                    problem += delay_var[jp][s_previousp] + earliest_dep_time(jp, s_previousp) + μ*y[j][jp][s] \
                     >= delay_var[j][s] + earliest_dep_time(j, s) + tau('pass', j, s, s_previousp)


def minimal_stay(problem, delay_var, S, train_sets):
    "minimum stay condition"
    for j in train_sets["J"]:
        for s in S[j]:

            s_previous = previous_station(S, j, s)

            if (s_previous != None and s != not_considered_station[j]):
                problem += delay_var[j][s]  >= delay_var[j][s_previous]



def track_occuparion(problem, delay_var, y, S, train_sets, μ):
    "track occupation"
    for s in train_sets["Jtrack"].keys():
        js = train_sets["Jtrack"][s]
        for (j,jp) in itertools.combinations(js, 2):

            s_previous = previous_station(S, j, s)
            s_previousp = previous_station(S, jp, s)

            # the last condition is to keep an order if trains are folowwing one another
            if (s_previous == s_previousp and s_previous != None and occurs_as_pair(j, jp, train_sets["Jd"])):

                problem += y[j][jp][s] == y[j][jp][s_previous]

            if s_previousp != None:

                problem += delay_var[jp][s_previousp] + earliest_dep_time(jp, s_previousp)  + tau("pass", jp, s_previousp, s) + μ*(1-y[j][jp][s]) >= \
                 delay_var[j][s] + earliest_dep_time(j, s) + tau('res')

            if s_previous != None:

                problem += delay_var[j][s_previous] + earliest_dep_time(j, s_previous) + tau("pass", j, s_previous, s) + μ*y[j][jp][s] >= \
                     delay_var[jp][s] + earliest_dep_time(jp, s) + tau('res')



def objective(problem, delay_var, S, train_sets, d_max):
    "objective function"
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(i, j)/d_max for i in train_sets["J"] for j in S[i] if penalty_weights(i,j) !=0])


def return_delay_time(prob, j, s):

    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            delay = v.varValue
            time = v.varValue + earliest_dep_time(j, s)
            return delay, time
    return 0, 0

def impact_to_objective(prob, j,s, d_max):
    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            return penalty_weights(j,s)/d_max*v.varValue
    return 0.




def linear_varibles(train_sets, S, d_max):

    trains_inds = train_sets["J"]

    secondary_delays_var = dict()

    for train in train_sets["J"]:

        secondary_delays_var.update(pus.LpVariable.dicts("Delays", ([train], S[train]), 0, d_max, cat='Integer'))


    y = dict()

    all_trains = np.concatenate([train_sets["Josingle"], train_sets["Jd"]])


    for js in all_trains:
        train1 = []
        train2 = []
        no_station = []
        for pair in itertools.combinations(js, 2):
            train1.append(pair[0])
            train2.append(pair[1])

            no_station = common_path(S, pair[0], pair[1])[0:-1]
        if len(js) > 1:

            y1 = pus.LpVariable.dicts("y", (train1, train2, no_station), 0, 1, cat='Integer')

            update_dictofdicts(y, y1)

    for s in train_sets["Jtrack"].keys():

        for pair in itertools.combinations(train_sets["Jtrack"][s], 2):

            y1 = pus.LpVariable.dicts("y", ([pair[0]], [pair[1]], [s]), 0, 1, cat='Integer')

            update_dictofdicts(y, y1)

    return secondary_delays_var, y



def solve_linear_problem(train_sets, S, d_max, μ):

    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var, y = linear_varibles(train_sets, S, d_max)


    minimal_span(prob, secondary_delays_var, y, S, train_sets, μ)
    minimal_stay(prob, secondary_delays_var, S, train_sets)
    single_line(prob, secondary_delays_var, y, S, train_sets, μ)

    track_occuparion(prob, secondary_delays_var, y, S, train_sets, μ)

    objective(prob, secondary_delays_var, S, train_sets, d_max)

    prob.solve()

    return prob


def toy_problem_variables(train_sets, S, d_max, μ = 30.):

    prob = solve_linear_problem(train_sets, S, d_max, μ)

    print("d_1, t_1", return_delay_time(prob, 0,0))
    print("d_2, t_2", return_delay_time(prob, 1,0))
    print("d_3, 3_3", return_delay_time(prob, 2,1))

    print("d_1', t_1'", return_delay_time(prob, 0,1))


    print("impact to objective t_1", impact_to_objective(prob, 0,0, d_max))
    print("impact to objective t_2", impact_to_objective(prob, 1,0, d_max))
    print("impact to objective t_3", impact_to_objective(prob, 2,1, d_max))




if True:
    toy_problem_variables(train_sets, S, 10)

    ### rerouting ####
    train_sets = {
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    toy_problem_variables(train_sets, S, 10)


#####   QUBO implementation #########

##### again default setting #####
train_sets = {
  "J": [0,1,2],
  "Jd": [[0,1], [2]],
  "Josingle": [],
  "Jround": dict(),
  "Jtrack": {1: [0,1]},
  "Jswitch": dict()
}


def indexing4qubo(train_sets, S, d_max):
    inds = []
    for j in train_sets["J"]:
        for s in S[j]:
            if s != not_considered_station[j]:
                for d in range(d_max+1):
                    inds.append({"j":j,"s":s,"d":d})
    return inds, len(inds)


inds, q_bits = indexing4qubo(train_sets, S, 10)
#print(inds[0])

def penalty(k, inds, d_max):
    j = inds[k]["j"]
    s = inds[k]["s"]
    w = penalty_weights(j, s)/d_max
    return inds[k]["d"] * w


def Psum(k, k1, inds):
    if inds[k]["j"] == inds[k1]["j"] and inds[k]["s"] == inds[k1]["s"]:
        if inds[k]["d"] == inds[k1]["d"]:
            return - 1.0
        else:
            return 1.0
    return 0.

def Pspan(k, k1, inds, train_sets, S):
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    if occurs_as_pair(j, j1, train_sets["Jd"]):
        s = inds[k]["s"]
        s1 = inds[k1]["s"]


        s_next = subsequent_station(S, j, s)
        s_nextp = subsequent_station(S, j1, s1)

        if (s == s1 and s_next != None and s_next == s_nextp):

            t = inds[k]["d"] + earliest_dep_time(j, s)
            t1 = inds[k1]["d"] + earliest_dep_time(j1, s)

            A =  - tau('blocks', j1, s, s_next) - max(0, tau('pass', j1, s, s_next) - tau('pass', j, s, s_next))

            B =  tau('blocks', j, s, s_next) + max(0, tau('pass', j, s, s_next) - tau('pass', j1, s, s_next))


            if A < t1-t < B:
                return 1.
    return 0.



def Pstay(k, k1, inds, train_sets, S):
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    if j == j1:
        s = inds[k]["s"]
        s1 = inds[k1]["s"]

        if s1 == subsequent_station(S, j, s):
            if inds[k]["d"] > inds[k1]["d"]:
                return 1.0

        if s == subsequent_station(S, j, s1):
            if inds[k1]["d"] > inds[k]["d"]:
                return 1.0

    return 0.


def P1track(k, k1, inds, train_sets, S):
    j = inds[k]["j"]
    j1 = inds[k1]["j"]

    if occurs_as_pair(j, j1, train_sets["Josingle"]):
        s = inds[k]["s"]
        s1 = inds[k1]["s"]

        t = inds[k]["d"] + earliest_dep_time(j, s)
        t1 = inds[k1]["d"] + earliest_dep_time(j1, s1)

        if s1 == subsequent_station(S, j, s):

            if - tau('pass', j1, s1 , s) < t1 - t < tau('pass', j, s , s1):

                    return 1.0

        if s == subsequent_station(S, j1, s1):

            if - tau('pass', j, s , s1) < t - t1 < tau('pass', j1, s1 , s):

                    return 1.0

    return 0.


if False:
    ### should be zero
    print(inds[3])
    print(inds[22])
    print(Pspan(3, 22, inds, train_sets, S))

    print(Pspan(22, 3, inds, train_sets, S))


    ### should be one
    print(inds[2])
    print(inds[22])
    print(Pspan(2, 22, inds, train_sets, S))

    print(Pspan(22, 2, inds, train_sets, S))


    print(Pstay(0, 0, inds, train_sets, S))


    ### should be one ###
    print(inds[2])
    print(inds[11])


    print(Pstay(2, 11, inds, train_sets, S))
    print(Pstay(11, 2, inds, train_sets, S))



    ### should be zero ###
    print(inds[1])
    print(inds[12])


    print(Pstay(1, 12, inds, train_sets, S))
    print(Pstay(12, 1, inds, train_sets, S))



### rerouting ####
train_sets = {
  "J": [0,1,2],
  "Jd": [],
  "Josingle": [[1,2], []],
  "Jround": dict(),
  "Jtrack": {1: [0,1]},
  "Jswitch": dict()
}


def z_indices(train_sets, S, d_max):
    inds = []
    for s in train_sets["Jtrack"].keys():
        for (j, j1) in itertools.combinations(train_sets["Jtrack"][s], 2):

            for d in range(d_max+1):
                for d1 in range(d_max+1):
                    inds.append({"j":j,"j1":j1,"s":s,"d":d, "d1":d1})
    return inds, len(inds)

inds_z, l = z_indices(train_sets, S, 10)

print(l == 121)


inds1 = np.concatenate([inds, inds_z])
print(len(inds1) == 176)

def P1qubic(k, k1, inds1, train_sets, S):
    # x with z
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:


        jx = inds[k]["j"]
        sx = inds1[k]["s"]
        sz = inds1[k1]["s"]
        if sz == subsequent_station(S, jx, sx):

            jz = inds1[k1]["j"]
            jz1 = inds1[k1]["j1"]

            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):

                # jz, jz1, tx => j', j, j', according to Eq 32
                # tz, tz1, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(jz, sz)
                tz1 = inds1[k1]["d1"] + earliest_dep_time(jz1, sz)


                if tx + tau("pass", jx, sx, sz) - tau("res", jz1, jz, sz) < tz1 <= tz:
                    return 1.


            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):


                # jz1, jz, tx => j', j, j', according to Eq 32
                # tz1, tz, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(jz, sz)
                tz1 = inds1[k1]["d1"] + earliest_dep_time(jz1, sz)


                if tx + tau("pass", jx, sx, sz) - tau("res", jz, jz1, sz) < tz <= tz1:
                    return 1.


    if len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        jx = inds[k1]["j"]

        sx = inds1[k1]["s"]
        sz = inds1[k]["s"]
        if sz == subsequent_station(S, jx, sx):

            jz = inds1[k]["j"]
            jz1 = inds1[k]["j1"]



            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):


                tx = inds1[k1]["d"] + earliest_dep_time(jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(jz1, sz)

                if tx + tau("pass", jx, sx, sz) - tau("res", jz1, jz, sz) < tz1 <= tz:
                    return 1.


            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):


                tx = inds1[k1]["d"] + earliest_dep_time(jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(jz1, sz)

                if tx + tau("pass", jx, sx, sz) - tau("res", jz, jz1, sz) < tz <= tz1:
                    return 1.

    return 0.


def h(x,y,z):
    return 3*z**2+ x * y - 2 *x * z - 2 * y * z


def P2qubic(k, k1, inds1, train_sets, S):
    # diagonal for z-ts
    if len(inds1[k].keys()) == len(inds1[k1].keys()) == 5:
        if k == k1:
            return 3.
    # x vs z
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:


        jx = inds[k]["j"]
        sx = inds1[k]["s"]
        sz = inds1[k1]["s"]
        if sz == subsequent_station(S, jx, sx):

            jz = inds1[k1]["j"]
            jz1 = inds1[k1]["j1"]

            # -1 because of the symmetrisation

            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):
                return -1.
            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):
                return -1.

    # z vs x
    if len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        jx = inds[k1]["j"]
        sx = inds1[k1]["s"]
        sz = inds1[k]["s"]
        if sz == subsequent_station(S, jx, sx):

            jz = inds1[k]["j"]
            jz1 = inds1[k]["j1"]

            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):
                return -1.
            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):
                return -1.
    # x vs x
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 3:
        s = inds1[k]["s"]
        if s == inds1[k1]["s"]:
            j = inds1[k]["j"]
            j1 = inds1[k]["j"]
            sz = subsequent_station(S, j, s)
            if  occurs_as_pair(j, j1, [train_sets["Jtrack"][sz]]):
                return 0.5

    return 0.



def get_coupling(k, k1, train_sets, S, inds, p_sum, p_pair):
    # add penalities
    J = p_sum*Psum(k, k1, inds)
    J += p_pair*Pspan(k, k1, inds, train_sets, S)
    J += p_pair*Pstay(k, k1, inds, train_sets, S)
    J += p_pair*P1track(k, k1, inds, train_sets, S)
    return J


def get_z_coupling(k, k1, train_sets, S, inds, p_pair, p_qubic):

    J = p_pair*P1qubic(k, k1, inds, train_sets, S)
    J += P1qubic(k, k1, inds, train_sets, S)
    return J

def make_Q(train_sets, S, d_max, p_sum, p_pair, p_qubic):
    inds, q_bits = indexing4qubo(train_sets, S, d_max)
    inds_z, q_bits_z = z_indices(train_sets, S, 10)

    inds1 = np.concatenate([inds, inds_z])

    l = q_bits
    l1 = q_bits+q_bits_z
    print(l1)
    Q = [[0. for _ in range(l1)] for _ in range(l1)]

    for k in range(l):
        Q[k][k] += penalty(k, inds, d_max)

    for k in range(l):
        for k1 in range(l):
            Q[k][k1] += get_coupling(k, k1, train_sets, S, inds, p_sum, p_pair)

    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(k, k1, train_sets, S, inds1, p_pair, p_qubic)

    return Q



Q = make_Q(train_sets, S, 10, 2.5, 2.5, 1.5)

#np.savez("Qfile.npz", Q=Q)

solution = np.load("solution.npz")




inds, q_bits = indexing4qubo(train_sets, S, 10)
l = q_bits


print(solution[0:l-1])


for i in range(l):
    if solution[i] == 1:
        print(inds[i])


if False:
    #### this should be zero #######

    print(inds1[1])
    print(inds1[70])
    print(P1qubic(1, 70, inds1, train_sets, S))
    print(P1qubic(70, 1, inds1, train_sets, S))

    #### this should be one #######

    print(inds1[1])
    print(inds1[100])
    print(P1qubic(1, 100, inds1, train_sets, S))
    print(P1qubic(100, 1, inds1, train_sets, S))

    print(inds1[22])
    print(inds1[107])
    print(P1qubic(22, 107, inds1, train_sets, S))
    print(P1qubic(107, 22, inds1, train_sets, S))

    ###  hs ####

    print("............ hs  ............")

    print(P2qubic(107, 107, inds1, train_sets, S))
    print(P2qubic(107, 108, inds1, train_sets, S))


    print(inds1[10])
    print(inds1[107])
    print(P2qubic(10, 107, inds1, train_sets, S))


    print(inds1[1])
    print(inds1[22])
    print(P2qubic(1, 22, inds1, train_sets, S))



    print(".....  1 track  ......")

    print(inds[22])
    print(inds[44])

    ### should be 1  ####
    print(P1track(22, 44, inds, train_sets, S))
    print(P1track(44, 22, inds, train_sets, S))


    print(inds[28])
    print(inds[44])

    print(P1track(28, 44, inds, train_sets, S))
    print(P1track(44, 28, inds, train_sets, S))

    print(inds[32])
    print(inds[44])

    print(P1track(32, 44, inds, train_sets, S))
    print(P1track(44, 32, inds, train_sets, S))


    ### should be 0  ####

    print(inds[23])
    print(inds[46])

    print(P1track(23, 46, inds, train_sets, S))
    print(P1track(46, 23, inds, train_sets, S))


    print(inds[22])
    print(inds[45])

    print(P1track(22, 45, inds, train_sets, S))
    print(P1track(45, 22, inds, train_sets, S))
