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


def test_performing_small_Qmat():
    #####   very simple problem two trains going one way ########


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

    inds, q_bits = indexing4qubo(train_sets, d_max)

    #(d_max+1) * 2 trains * 2 stations
    assert q_bits == 6*2*2

    assert np.shape(Q) == (6*2*2, 6*2*2)

    M = np.matrix(Q)

    assert np.array_equal(np.transpose(M), M)

    # diagonal, delay penalties and linear tem penalties
    # J0 leaves S0 -p_sum + 0.4 for each late minute

    k = inds.index({'j': 0, 's': 0, 'd': 0})
    assert Q[k][k] == -2
    k = inds.index({'j': 0, 's': 0, 'd': 1})
    assert Q[k][k] == -1.6
    k = inds.index({'j': 0, 's': 0, 'd': 2})
    assert Q[k][k] == -1.2

    # J1 leaves S0 -p_sum +  0.1 for each late minute
    k = inds.index({'j': 1, 's': 0, 'd': 0})
    assert Q[k][k] == -2
    k = inds.index({'j': 1, 's': 0, 'd': 1})
    assert Q[k][k] == -1.9

    # J1 and J0 leaves to close to each other, p_pair
    k = inds.index({'j': 0, 's': 0, 'd': 0})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})
    assert Q[k][k1] == 1.
    k = inds.index({'j': 0, 's': 0, 'd': 1})
    assert Q[k][k1] == 1.
    k = inds.index({'j': 0, 's': 0, 'd': 2})
    assert Q[k][k1] == 1.



    ####  two trains going in opposite ways ######

    taus = {"pass" : {"0_0_1" : 4, "1_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_1_0" : 2}, "stop": {"0_1_None" : 1, "1_0_None" : 1}, "res": 1}
    timetable = {"tau": taus,
                  "initial_conditions" : {"0_0" : 3, "1_1" : 1},
                  "penalty_weights" : {"0_0" : 2, "1_1" : 0.5}}

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


    Q = make_Q(train_sets, timetable, d_max, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.shape(Q) == (6*2*2, 6*2*2)

    M = np.matrix(Q)

    assert np.array_equal(np.transpose(M), M)

    inds, q_bits = indexing4qubo(train_sets, d_max)

    # diagonal, delay penalties and linear tem penalties
    # J0 leaves S0 -p_sum + 0.4 for each late minute

    k = inds.index({'j': 0, 's': 0, 'd': 0})
    assert Q[k][k] == -2
    k = inds.index({'j': 0, 's': 0, 'd': 1})
    assert Q[k][k] == -1.6
    k = inds.index({'j': 0, 's': 0, 'd': 2})
    assert Q[k][k] == -1.2

    # J1 leaves S1 -p_sum +  0.1 for each late minute
    k = inds.index({'j': 1, 's': 1, 'd': 0})
    assert Q[k][k] == -2
    k = inds.index({'j': 1, 's': 1, 'd': 1})
    assert Q[k][k] == -1.9

    # trains starts in opposite directions in such a way that they would meet on the single track

    k = inds.index({'j': 0, 's': 0, 'd': 0})
    k1 = inds.index({'j': 1, 's': 1, 'd': 0})
    assert Q[k][k1] == 1.
    assert Q[k1][k] == 1.


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
test_performing_small_Qmat()
test_performing_Qmat()


print("tests done")
