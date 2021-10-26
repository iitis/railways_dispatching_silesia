import itertools

import numpy as np

from .helpers_functions import *


def indexing4qubo(train_sets, d_max):
    "returns vector of dicts containing trains, stations and delays"
    "the index of vector correspond to the index on particulat train station and delay in Q matrix"
    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]
    inds = []
    for j in train_sets["J"]:
        for s in S[j]:
            if s != not_considered_station[j]:
                for d in range(d_max+1):
                    inds.append({"j": j, "s": s, "d": d})
    return inds, len(inds)


def Psum(k, k1, inds):
    "given the vector of dicts from indexing4qubo(train_sets, d_max) and particular indices"
    "returns the not wieghted contribution to Q matrix from ∑_i x_i  = 1 constrain"
    if inds[k]["j"] == inds[k1]["j"] and inds[k]["s"] == inds[k1]["s"]:
        if inds[k]["d"] == inds[k1]["d"]:
            return - 1.0
        else:
            return 1.0
    return 0.


def Pspan(timetable, k, k1, inds, train_sets):
    "returns not weighted contribution to Q from the minimal span condition constrain, here additionaly train paths are necessary"

    " ..... j1 -> ....... j2 -> ....."
    "              span              "

    S = train_sets["Paths"]

    j = inds[k]["j"]
    j1 = inds[k1]["j"]

    s = inds[k]["s"]
    s1 = inds[k1]["s"]

    s_next = subsequent_station(S[j], s)
    s_nextp = subsequent_station(S[j1], s1)

    if (s == s1 and s_next != None and s_next == s_nextp):
        print(".................")

        if s in train_sets["Jd"].keys():
            if s_next in train_sets["Jd"][s].keys():
                if occurs_as_pair(j, j1, train_sets["Jd"][s][s_next]):


                    t = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
                    t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s)

                    A = -tau(timetable, 'blocks', first_train=j1, second_train=j, first_station=s, second_station=s_next)

                    B = tau(timetable, 'blocks', first_train=j, second_train=j1, first_station=s, second_station=s_next)

                    if A < t1-t < B:
                        return 1.
    return 0.


def Pstay(timetable, k, k1, inds, train_sets):
    "returns not weighted contribution to Q from the minimal stay condition constrain, here additionaly train paths are necessary"
    S = train_sets["Paths"]

    j = inds[k]["j"]
    if j == inds[k1]["j"]:
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
    "returns not weighted contribution to Q from the single track line condition constrain, here additionaly train paths are necessary"
    " ......                            ......  "
    "       \                          /        "
    " .j1 ->............................. <-j2.."
    "switch occupancy condition from the single line is included"
    "  ------         "
    "         \       "
    "---------  c ----"
    S = train_sets["Paths"]

    j = inds[k]["j"]
    j1 = inds[k1]["j"]

    if occurs_as_pair(j, j1, train_sets["Josingle"]):
        s = inds[k]["s"]
        s1 = inds[k1]["s"]

        t = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
        t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)

        if s1 == subsequent_station(S[j], s):
            if -tau(timetable, 'res') - tau(timetable, 'pass', first_train=j1, first_station=s1, second_station=s) < t1 - t:
                if t1-t < tau(timetable, 'pass', first_train=j, first_station=s, second_station=s1) + tau(timetable, 'res'):
                    return 1.0

        if s == subsequent_station(S[j1], s1):
            if -tau(timetable, 'res') - tau(timetable, 'pass', first_train=j, first_station=s, second_station=s1) < t - t1:
                if t - t1 < tau(timetable, 'pass', first_train=j1, first_station=s1, second_station=s) + tau(timetable, 'res'):
                    return 1.0

    return 0.

# TODO  circulation condition  and swotch occupancy condition (if not included in single line and later in track occupancy)


def z_indices(train_sets, d_max):
    "returns a vector of dicts consisten with auxiliary variable used to decompose 3'rd order terms"
    "used to handle track occupancy condition, dicts contains two trains, a station where the condition is checked"
    "and delays of this two trains"
    inds = []
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, j1) in itertools.combinations(js, 2):
                for d in range(d_max+1):
                    for d1 in range(d_max+1):
                        inds.append({"j": j, "j1": j1, "s": s, "d": d, "d1": d1})
    return inds, len(inds)


def P1qubic(timetable, k, k1, inds1, train_sets):
    "returns not weighted contribution to Q from the single track occupancy conditions constrains, auxiliary variables are included"
    S = train_sets["Paths"]
    # x with z
    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:
        jx = inds1[k]["j"]
        sx = inds1[k]["s"]
        sz = inds1[k1]["s"]
        if sz == subsequent_station(S[jx], sx):
            jz = inds1[k1]["j"]
            jz1 = inds1[k1]["j1"]

            #print(train_sets["Jtrack"][sz])

            if (jx == jz) and occurs_as_pair(jx, jz1, train_sets["Jtrack"][sz]):
                # jz, jz1, tx => j', j, j', according to Eq 32
                # tz, tz1, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k1]["d1"] + \
                    earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz) - tau(timetable, "res") < tz1 <= tz:
                    return 1.

            if (jx == jz1) and occurs_as_pair(jx, jz, train_sets["Jtrack"][sz]):
                # jz1, jz, tx => j', j, j', according to Eq 32
                # tz1, tz, tx => t', t,  t'' according to Eq 32
                # sx, sz -> s', s

                tx = inds1[k]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k1]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k1]["d1"] + \
                    earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz) - tau(timetable, "res") < tz <= tz1:
                    return 1.

    if len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        jx = inds1[k1]["j"]
        sx = inds1[k1]["s"]
        sz = inds1[k]["s"]
        if sz == subsequent_station(S[jx], sx):
            jz = inds1[k]["j"]
            jz1 = inds1[k]["j1"]

            if (jx == jz) and occurs_as_pair(jx, jz1, train_sets["Jtrack"][sz]):
                tx = inds1[k1]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz) - tau(timetable, "res") < tz1 <= tz:
                    return 1.

            if (jx == jz1) and occurs_as_pair(jx, jz, train_sets["Jtrack"][sz]):
                tx = inds1[k1]["d"] + earliest_dep_time(S, timetable, jx, sx)
                tz = inds1[k]["d"] + earliest_dep_time(S, timetable, jz, sz)
                tz1 = inds1[k]["d1"] + earliest_dep_time(S, timetable, jz1, sz)

                if tx + tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz) - tau(timetable, "res") < tz <= tz1:
                    return 1.
    return 0.


def P2qubic(k, k1, inds1, train_sets):
    "returns not weighted contribution to Q from constrains inposed on the auxilairy variables by the Rosenberg polynomial approach "
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
                if occurs_as_pair(j, j1, train_sets["Jtrack"][s]):
                    return 0.5
    return 0.


def penalty(timetable, k, inds, d_max):
    "returns weighted contribution to Q from the objective penalties"
    j = inds[k]["j"]
    s = inds[k]["s"]
    w = penalty_weights(timetable, j, s)/d_max
    return inds[k]["d"] * w


def get_coupling(timetable, k, k1, train_sets, inds, p_sum, p_pair):
    "returns hard constrains elements of Q matrix in the case where no auxiliary variables are included"
    J = p_sum*Psum(k, k1, inds)
    J += p_pair*Pspan(timetable, k, k1, inds, train_sets)
    J += p_pair*Pstay(timetable, k, k1, inds, train_sets)
    J += p_pair*P1track(timetable, k, k1, inds, train_sets)
    return J


def get_z_coupling(timetable, k, k1, train_sets, inds, p_pair, p_qubic):
    "returns hard constrains elements of Q matrix in the case where auxiliary variables are included"
    J = p_pair*P1qubic(timetable, k, k1, inds, train_sets)
    J += p_qubic*P2qubic(k, k1, inds, train_sets)
    return J


def make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_q, p_qubic):
    "returns Q matrix"
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
            Q[k][k1] += get_coupling(timetable, k, k1,
                                     train_sets, inds, p_sum, p_pair)
    for k in range(l1):
        for k1 in range(l1):
            Q[k][k1] += get_z_coupling(timetable, k,
                                       k1, train_sets, inds1, p_pair_q, p_qubic)
    return Q
