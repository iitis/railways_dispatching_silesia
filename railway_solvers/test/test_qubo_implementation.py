import sys
import numpy as np

sys.path.append('../src')

from make_qubo import *

#from input_data import small_timetable

taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8, "2_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_None" : 1, "1_1_None" : 1}, "res": 1}
timetable = {"tau": taus,
              "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
              "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}

### testing particular QUBO element cration


def energy(v, Q):
    if -1 in v:
        v = [(y+1)/2 for y in v]
    X = np.matrix(Q)
    V = np.matrix(v)
    return V*X*V.transpose()



def test_pspan_pstay_p1track():

    # default


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

    inds, q_bits = indexing4qubo(train_sets, 10)


    k = inds.index({'j': 0, 's': 0, 'd': 3})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    assert Pspan(timetable, k, k1, inds, train_sets) == 0.

    assert Pspan(timetable, k1, k, inds, train_sets) == 0.



    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    assert Pspan(timetable, k, k1, inds, train_sets) == 1.
    assert Pspan(timetable, k1, k, inds, train_sets) == 1.


    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 0, 's': 1, 'd': 0})

    assert Pstay(timetable, k, k1, inds, train_sets) == 1.
    assert Pstay(timetable, k1, k, inds, train_sets) == 1.


    k = inds.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds.index({'j': 0, 's': 1, 'd': 1})


    assert Pstay(timetable, k, k1, inds, train_sets) == 0.
    assert Pstay(timetable, k1, k, inds, train_sets) == 0.

    ### rerouting ####
    train_sets_r = {
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

    ### .....  1 track  ......


    k = inds.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.


    k = inds.index({'j': 1, 's': 0, 'd': 6})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.

    k = inds.index({'j': 1, 's': 0, 'd': 10})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 1.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 1.



    k = inds.index({'j': 1, 's': 1, 'd': 1})
    k1 = inds.index({'j': 0, 's': 0, 'd': 2})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 0.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 0.


    k = inds.index({'j': 1, 's': 1, 'd': 0})
    k1 = inds.index({'j': 2, 's': 1, 'd': 1})

    assert P1track(timetable, k, k1, inds, train_sets_r) == 0.
    assert P1track(timetable, k1, k, inds, train_sets_r) == 0.




def test_qubic():


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



    inds, q_bits = indexing4qubo(train_sets, 10)
    inds_z, l = z_indices(train_sets, 10)

    assert l == 121


    inds1 = list(np.concatenate([inds, inds_z]))
    assert len(inds1) == 176

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 1, 'd1': 4})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 0.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 0.

    #### this should be one #######

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 1.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 1.

    k = inds1.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    assert P1qubic(timetable, k, k1, inds1, train_sets) == 1.
    assert P1qubic(timetable, k1, k, inds1, train_sets) == 1.

    ###  P2qubic ####


    k = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 2})

    assert P2qubic(k, k, inds1, train_sets) == 3.
    assert P2qubic(k, k1, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': 0, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets) == 0.

    k = inds1.index({'j': 0, 's': 1, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 10, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets) == -1.
    assert P2qubic(k1, k, inds1, train_sets) == -1.

    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 1, 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets) == 0.5
    assert P2qubic(k1, k, inds1, train_sets) == 0.5

    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 2, 's': 1, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.


    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.


    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets) == 0.
    assert P2qubic(k1, k, inds1, train_sets) == 0.



def test_penalties_and_couplings():


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
    p_qubic = 2.1

    d_max = 10

    inds, q_bits = indexing4qubo(train_sets, d_max)
    assert get_coupling(timetable, 0,0, train_sets, inds, p_sum, p_pair) == -2.5
    assert get_coupling(timetable, 0,24, train_sets, inds, p_sum, p_pair) == 1.25


    inds_z, l = z_indices(train_sets, d_max)
    inds1 = list(np.concatenate([inds, inds_z]))

    k = inds1.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    assert get_z_coupling(timetable, k, k1, train_sets, inds1, p_pair, p_qubic) == 1.25

    assert penalty(timetable, 1, inds, d_max) == 0.2


def simple_test_two_trains_going_one_way():

    taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_None" : 1, "1_1_None" : 1}, "res": 1}
    timetable = {"tau": taus,
                  "initial_conditions" : {"0_0" : 3, "1_0" : 1},
                  "penalty_weights" : {"0_0" : 2, "1_0" : 0.5}}

    train_sets = {
    "skip_station" : {
        0: None,
        1: None,
    },
    "Paths": {0: [0,1], 1: [0,1]},
    "J": [0,1],
    "Jd": [[0,1]],
    "Josingle": [],
    "Jround": dict(),
    "Jtrack": dict(),
    "Jswitch": dict()
    }

    p_sum = 2
    p_pair = 1.
    p_pair_qubic = 1.
    p_qubic = 2.
    d_max = 5


    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.array_equal(Q, np.load("files/Qfile_one_way.npz")["Q"])

    sol = np.load("files/solution_one_way.npz")

    assert energy(sol, Q) == -8+0.4



def simple_test_two_trains_going_opposite_ways():

    taus = {"pass" : {"0_0_1" : 4, "1_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_1_0" : 2}, "stop": {"0_1_None" : 1, "1_0_None" : 1}, "res": 1}
    timetable = {"tau": taus,
                  "initial_conditions" : {"0_0" : 3, "1_1" : 1},
                  "penalty_weights" : {"0_0" : 2., "1_1" : 0.5}}

    train_sets = {
    "skip_station" : {
        0: None,
        1: None,
    },
    "Paths": {0: [0,1], 1: [1,0]},
    "J": [0,1],
    "Jd": [],
    "Josingle": [[0,1]],
    "Jround": dict(),
    "Jtrack": dict(),
    "Jswitch": dict()
    }

    p_sum = 2.
    p_pair = 1.
    p_pair_qubic = 1.
    p_qubic = 2.
    d_max = 10


    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.array_equal(Q, np.load("files/Qfile_two_ways.npz")["Q"])

    sol = np.load("files/solution_two_ways.npz")

    assert energy(sol, Q)[0][0] == -8+0.35



def test_performing_Qmat():
    #####   dispatching problem that was solved on D-Wave   ########


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

    d_max = 10


    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.array_equal(Q, np.load("files/Qfile.npz")["Q"])

    train_sets_r = {
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

    Q_r = make_Q(train_sets_r, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.array_equal(Q_r, np.load("files/Qfile_r.npz")["Q"])



test_penalties_and_couplings()
test_pspan_pstay_p1track()
test_qubic()

# test on Q matrix
simple_test_two_trains_going_one_way()
simple_test_two_trains_going_opposite_ways()
test_performing_Qmat()


print("tests done")
