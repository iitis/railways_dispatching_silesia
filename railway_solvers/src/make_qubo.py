import itertools
import numpy as np
from helpers_functions import *

def indexing4qubo(train_sets, d_max):

    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]
    inds = []
    for j in train_sets["J"]:
        for s in S[j]:
            if s != not_considered_station[j]:
                for d in range(d_max+1):
                    inds.append({"j":j,"s":s,"d":d})
    return inds, len(inds)


def Psum(k, k1, inds):
    if inds[k]["j"] == inds[k1]["j"] and inds[k]["s"] == inds[k1]["s"]:
        if inds[k]["d"] == inds[k1]["d"]:
            return - 1.0
        else:
            return 1.0
    return 0.

def Pspan(timetable, k, k1, inds, train_sets):

    S = train_sets["Paths"]

    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    if occurs_as_pair(j, j1, train_sets["Jd"]):

        s = inds[k]["s"]
        s1 = inds[k1]["s"]


        s_next = subsequent_station(S[j], s)
        s_nextp = subsequent_station(S[j1], s1)

        if (s == s1 and s_next != None and s_next == s_nextp):

            t = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
            t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s)

            ofset_A = max(0, timetable["tau"]["pass"][str(j1)+"_"+str(s)+"_"+str(s_next)] - timetable["tau"]["pass"][str(j)+"_"+str(s)+"_"+str(s_next)])

            A =  - tau(timetable, 'blocks', j1, s, s_next) - max(0, tau(timetable, 'pass', j1, s, s_next) - tau(timetable, 'pass', j, s, s_next))

            B =  tau(timetable, 'blocks', j, s, s_next) + max(0, tau(timetable, 'pass', j, s, s_next) - tau(timetable, 'pass', j1, s, s_next))


            if A < t1-t < B:
                return 1.
    return 0.



def Pstay(timetable, k, k1, inds, train_sets):

    S = train_sets["Paths"]

    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    if j == j1:
        s = inds[k]["s"]
        s1 = inds[k1]["s"]

        if s1 == subsequent_station(S[j], s):
            if inds[k]["d"] > inds[k1]["d"]:
                return 1.0

        if s == subsequent_station(S[j], s1):
            if inds[k1]["d"] > inds[k]["d"]:
                return 1.0

    return 0.


def P1track(timetable, k, k1, inds, train_sets):

    S = train_sets["Paths"]


    j = inds[k]["j"]
    j1 = inds[k1]["j"]

    if occurs_as_pair(j, j1, train_sets["Josingle"]):
        s = inds[k]["s"]
        s1 = inds[k1]["s"]

        t = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
        t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)

        if s1 == subsequent_station(S[j], s):

            if - tau(timetable, 'res') - tau(timetable, 'pass', j1, s1 , s) < t1 - t < tau(timetable, 'pass', j, s , s1) + tau(timetable, 'res'):

                    return 1.0

        if s == subsequent_station(S[j1], s1):

            if - tau(timetable, 'res') - tau(timetable, 'pass', j, s , s1) < t - t1 < tau(timetable, 'pass', j1, s1 , s) + tau(timetable, 'res'):

                    return 1.0

    return 0.



def z_indices(train_sets, d_max):
    inds = []
    for s in train_sets["Jtrack"].keys():
        for (j, j1) in itertools.combinations(train_sets["Jtrack"][s], 2):

            for d in range(d_max+1):
                for d1 in range(d_max+1):
                    inds.append({"j":j,"j1":j1,"s":s,"d":d, "d1":d1})
    return inds, len(inds)



def P1qubic(timetable, k, k1, inds1, train_sets):

    S = train_sets["Paths"]
    # x with z
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:


        jx = inds1[k]["j"]
        sx = inds1[k]["s"]
        sz = inds1[k1]["s"]
        if sz == subsequent_station(S[jx], sx):

            jz = inds1[k1]["j"]
            jz1 = inds1[k1]["j1"]

            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):

                # jz, jz1, tx => j', j, j', according to Eq 32
                # tz, tz1, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k1]["d1"] + earliest_dep_time(S, timetable, jz1, sz)


                if tx + tau(timetable, "pass", jx, sx, sz) - tau(timetable, "res") < tz1 <= tz:
                    return 1.


            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):


                # jz1, jz, tx => j', j, j', according to Eq 32
                # tz1, tz, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k1]["d1"] + earliest_dep_time(S, timetable, jz1, sz)


                if tx + tau(timetable, "pass", jx, sx, sz) - tau(timetable, "res") < tz <= tz1:
                    return 1.


    if len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        jx = inds1[k1]["j"]

        sx = inds1[k1]["s"]
        sz = inds1[k]["s"]
        if sz == subsequent_station(S[jx], sx):

            jz = inds1[k]["j"]
            jz1 = inds1[k]["j1"]



            if (jx == jz) and occurs_as_pair(jx, jz1, [train_sets["Jtrack"][sz]]):


                tx = inds1[k1]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", jx, sx, sz) - tau(timetable, "res") < tz1 <= tz:
                    return 1.


            if (jx == jz1) and occurs_as_pair(jx, jz, [train_sets["Jtrack"][sz]]):


                tx = inds1[k1]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", jx, sx, sz) - tau(timetable, "res") < tz <= tz1:
                    return 1.

    return 0.


#def h(x,y,z):
#    return 3*z**2+ x * y - 2 *x * z - 2 * y * z


def P2qubic(k, k1, inds1, train_sets):

    S = train_sets["Paths"]


    # diagonal for z-ts
    if len(inds1[k].keys()) == len(inds1[k1].keys()) == 5:
        if k == k1:
            return 3.
    # x vs z
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:


        jx = inds1[k]["j"]
        sx = inds1[k]["s"]
        sz = inds1[k1]["s"]
        if sz == sx:

            jz = inds1[k1]["j"]
            jz1 = inds1[k1]["j1"]

            # -1 because of the symmetrisation

            if jx == jz:
                if inds1[k]["d"] == inds1[k1]["d"]:
                    return -1.
            if jx == jz1:
                if inds1[k]["d"] == inds1[k1]["d1"]:
                    return -1.

    # z vs x
    if len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        jx = inds1[k1]["j"]
        sx = inds1[k1]["s"]
        sz = inds1[k]["s"]
        if sz == sx:

            jz = inds1[k]["j"]
            jz1 = inds1[k]["j1"]

            if jx == jz:
                if inds1[k1]["d"] == inds1[k]["d"]:
                    return -1.

            if jx == jz1:
                if inds1[k1]["d"] == inds1[k]["d1"]:
                    return -1.
    # x vs x
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 3:
        s = inds1[k]["s"]
        if s == inds1[k1]["s"]:
            j = inds1[k]["j"]
            j1 = inds1[k1]["j"]
            sz = subsequent_station(S[j], s)
            if s in train_sets["Jtrack"].keys():
                if occurs_as_pair(j, j1, [train_sets["Jtrack"][s]]):
                    return 0.5

    return 0.

def penalty(timetable, k, inds, d_max):
    j = inds[k]["j"]
    s = inds[k]["s"]
    w = penalty_weights(timetable, j, s)/d_max
    return inds[k]["d"] * w

def get_coupling(timetable, k, k1, train_sets, inds, p_sum, p_pair):

    J = p_sum*Psum(k, k1, inds)
    J += p_pair*Pspan(timetable, k, k1, inds, train_sets)
    J += p_pair*Pstay(timetable, k, k1, inds, train_sets)
    J += p_pair*P1track(timetable, k, k1, inds, train_sets)
    return J


def get_z_coupling(timetable, k, k1, train_sets, inds, p_pair, p_qubic):

    J = p_pair*P1qubic(timetable, k, k1, inds, train_sets)
    J += p_qubic*P2qubic(k, k1, inds, train_sets)
    return J

def make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_q, p_qubic):

    inds, q_bits = indexing4qubo(train_sets, d_max)
    inds_z, q_bits_z = z_indices(train_sets, d_max)

    inds1 = np.concatenate([inds, inds_z])

    l = q_bits
    l1 = q_bits+q_bits_z

    Q = [[0. for _ in range(l1)] for _ in range(l1)]

    for k in range(l):
        Q[k][k] += penalty(timetable, k, inds, d_max)

    for k in range(l):
        for k1 in range(l):
            Q[k][k1] += get_coupling(timetable, k, k1, train_sets, inds, p_sum, p_pair)

    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(timetable, k, k1, train_sets, inds1, p_pair_q, p_qubic)


    return Q
