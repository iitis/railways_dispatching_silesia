import itertools

import numpy as np

from .helpers_functions import *


def indexing4qubo(train_sets, d_max):
    "returns vector of dicts containing trains, stations and delays"
    "the index of vector correspond to the index on particulat train station and delay in Q matrix"

    S = train_sets["Paths"]
    inds = []
    for j in train_sets["J"]:
        for s in S[j]:
            if s != train_sets["skip_station"][j]:
                for d in range(d_max+1):
                    inds.append({"j": j, "s": s, "d": d})
    return inds, len(inds)


##### summ to one constrain #####

def Psum(k, k1, inds):
    "given the vector of dicts from indexing4qubo(train_sets, d_max) and particular indices"
    "returns the not wieghted contribution to Q matrix from ∑_i x_i  = 1 constrain"
    if inds[k]["j"] == inds[k1]["j"] and inds[k]["s"] == inds[k1]["s"]:
        if inds[k]["d"] == inds[k1]["d"]:
            return - 1.0
        else:
            return 1.0
    return 0.


#  constrains from dispatching

#####  minimal span constrain #######

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

    if (s == s1 and s_next != None and s_next == subsequent_station(S[j1], s1)):

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

#### single track line and deadlock constrain ######

def penalty_single_track_condition(timetable, k, k1, inds, train_sets):
    S = train_sets["Paths"]
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    s = inds[k]["s"]
    s1 = inds[k1]["s"]

    if not_the_same_rolling_stock(j, j1, train_sets):

        if (s, s1) in train_sets["Josingle"].keys() and [j, j1] in train_sets["Josingle"][(s, s1)]:
            t = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
            t2 = t
            t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)

            t += - tau(timetable, 'pass', first_train=j1, first_station=s1, second_station=s)
            t2 += tau(timetable, 'pass', first_train=j, first_station=s, second_station=s1)

            if t < t1 < t2:
                return 1.0
    return 0.

def P1track(timetable, k, k1, inds, train_sets):
    "returns not weighted contribution to Q from the single track line condition constrain, here additionaly train paths are necessary"
    " ......                            ......  "
    "       \                          /        "
    " .j1 ->............................. <-j2.."

    p = penalty_single_track_condition(timetable, k, k1, inds, train_sets)
    p += penalty_single_track_condition(timetable, k1, k, inds, train_sets)
    return p

#### minimal stay constrain ######

def penalty_for_minimal_stay_condition(timetable, k, k1, inds, train_sets):
    S = train_sets["Paths"]
    j = inds[k]["j"]

    if j == inds[k1]["j"]:
        sp = inds[k]["s"]
        s = inds[k1]["s"]
        if s == subsequent_station(S[j], sp):
            LHS = inds[k1]["d"]
            LHS += earliest_dep_time(S, timetable, j, s)

            RHS = inds[k]["d"]
            RHS += earliest_dep_time(S, timetable, j, sp)
            RHS +=  tau(timetable, 'pass', first_train=j, first_station=sp, second_station=s)
            RHS +=  tau(timetable, 'stop', first_train=j, first_station=s)

            #if inds[k]["d"] > inds[k1]["d"]:
            if LHS < RHS:  # timetable is ensured by nono-zero delay
                return 1.0
    return 0.


def Pstay(timetable, k, k1, inds, train_sets):
    "returns not weighted contribution to Q from the minimal stay condition constrain, here additionaly train paths are necessary"
    p = penalty_for_minimal_stay_condition(timetable, k, k1, inds, train_sets)
    p += penalty_for_minimal_stay_condition(timetable, k1, k, inds, train_sets)
    return p


#####  single track occupation  at station condition #####


def z_indices(train_sets, d_max):
    "returns a vector of dicts consisten with auxiliary variable used to decompose 3'rd order terms"
    "used to handle track occupancy condition, dicts contains two trains, a station where the condition is checked"
    "and delays of this two trains"
    inds = []
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, j1) in itertools.combinations(js, 2):
                if not_the_same_rolling_stock(j, j1, train_sets):
                    for d in range(d_max+1):
                        for d1 in range(d_max+1):
                            inds.append({"j": j, "j1": j1, "s": s, "d": d, "d1": d1})
    return inds, len(inds)



def one_track_constrains(jx, jz, jz1, sx, sz, d, d1, d2, train_sets, timetable):

    S = train_sets["Paths"]

    tx = d + earliest_dep_time(S, timetable, jx, sx)
    tx += tau(timetable, "pass", first_train=jx, first_station=sx, second_station=sz)
    if "add_swithes_at_s" in train_sets.keys():
        if sz in train_sets["add_swithes_at_s"]:  # this is the approximation used in  ArXiv:2107.03234,
            tx -= tau(timetable, "res")
    tz = d1 + earliest_dep_time(S, timetable, jz, sz)
    tz1 = d2 + earliest_dep_time(S, timetable, jz1, sz)

    if tx < tz1 <= tz:
        return 1.
    return 0.

def pair_of_one_track_constrains(inds1, k, k1, train_sets, timetable):

    S = train_sets["Paths"]

    jx = inds1[k]["j"]
    sx = inds1[k]["s"]
    sz = inds1[k1]["s"]
    d =  inds1[k]["d"]
    d1 =  inds1[k1]["d"]
    d2 = inds1[k1]["d1"]

    if sz == subsequent_station(S[jx], sx):
        jz = inds1[k1]["j"]
        jz1 = inds1[k1]["j1"]

        if (jx == jz) and occurs_as_pair(jx, jz1, train_sets["Jtrack"][sz]):
            # jz, jz1, tx => j', j, j', according to Eq 32
            # tz, tz1, tx => t', t,  t'' according to Eq 32
            # sx, sz -> s', s

            p = one_track_constrains(jx, jz, jz1, sx, sz, d, d1, d2, train_sets, timetable)
            if p > 0:
                return p

        if (jx == jz1) and occurs_as_pair(jx, jz, train_sets["Jtrack"][sz]):
            # jz1, jz, tx => j', j, j', according to Eq 32
            # tz1, tz, tx => t', t,  t'' according to Eq 32
            # sx, sz -> s', s

            p = one_track_constrains(jx, jz1, jz, sx, sz, d, d2, d1, train_sets, timetable)
            if p > 0:
                return p
    return 0




def P1qubic(timetable, k, k1, inds1, train_sets):
    "returns not weighted contribution to Q from the single track occupancy conditions constrains, auxiliary variables are included"
    S = train_sets["Paths"]
    # if trains have the same rolling stock we are not checking
    if not not_the_same_rolling_stock(inds1[k]["j"], inds1[k1]["j"], train_sets):
        return 0.

    if len(inds1[k].keys()) == 3 and len(inds1[k1].keys()) == 5:
        return pair_of_one_track_constrains(inds1, k, k1, train_sets, timetable)

    elif len(inds1[k].keys()) == 5 and len(inds1[k1].keys()) == 3:
        return pair_of_one_track_constrains(inds1, k1, k, train_sets, timetable)

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


def p_circ(timetable, k, k1, inds, train_sets):

    S = train_sets["Paths"]
    j = inds[k]["j"]
    j1 = inds[k1]["j"]
    s = inds[k]["s"]
    s1 = inds[k1]["s"]

    if s1 in train_sets["Jround"].keys():
        if previous_station(S[j], s1) == s:
            if [j, j1] in train_sets["Jround"][s1]:
                LHS = inds[k]["d"] + earliest_dep_time(S, timetable, j, s)
                LHS += tau(timetable, 'prep', first_train=j1, first_station=s1)
                LHS += tau(timetable, 'pass', first_train=j, first_station=s, second_station=s1)
                RHS = inds[k1]["d"] + earliest_dep_time(S, timetable, j1, s1)
                if LHS > RHS:
                    return 1.0
    return 0.

def Pcirc(timetable, k, k1, inds, train_sets):
    "returns not weighted penalty for circulation condition"

    p = p_circ(timetable, k, k1, inds, train_sets)
    p += p_circ(timetable, k1, k, inds, train_sets)
    return p

# there is a redundant semetrisation and desymerisation, ot can be simplified
def p_switch(timetable, k, k1, inds, train_sets):

    S = train_sets["Paths"]
    jp = inds[k]["j"]
    jpp = inds[k1]["j"]
    sp = inds[k]["s"]
    spp = inds[k1]["s"]

    if not_the_same_rolling_stock(jp, jpp, train_sets):

        for s in train_sets["Jswitch"].keys():

            for pairs_of_switch in train_sets["Jswitch"][s]:

                if (jp == list(pairs_of_switch.keys())[0]) and (jpp == list(pairs_of_switch.keys())[1]):

                    if sp == departure_station4switches(s, jp, pairs_of_switch, train_sets):

                        if spp == departure_station4switches(s, jpp, pairs_of_switch, train_sets):

                            t = inds[k]["d"] + earliest_dep_time(S, timetable, jp, sp)
                            if s != sp:
                                t += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)

                            t1 = inds[k1]["d"] + earliest_dep_time(S, timetable, jpp, spp)
                            if s != spp:
                                t1 += tau(timetable, 'pass', first_train=jpp, first_station=spp, second_station=s)

                            if -tau(timetable, 'res')  < t1-t <  tau(timetable, 'res'):
                                return 1.0
    return 0.



def Pswitch(timetable, k, k1, inds, train_sets):

    "switch occupancy condition"
    "  ------         "
    "         \       "
    "---------  c ----"

    p = p_switch(timetable, k, k1, inds, train_sets)
    p += p_switch(timetable, k1, k, inds, train_sets)
    return  p





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
    J += p_pair*Pcirc(timetable, k, k1, inds, train_sets)
    J += p_pair*Pswitch(timetable, k, k1, inds, train_sets)
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
