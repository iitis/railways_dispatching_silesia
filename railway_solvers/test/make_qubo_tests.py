import sys
import numpy as np

sys.path.append('../src')

from make_qubo import *




### testing particular QUBO element cration


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


def test_pspan_pstay_p1track(S, not_considered_station):

    # default

    train_sets = {
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }

    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)


    k = inds.index({'j': 0, 's': 0, 'd': 3})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    assert Pspan(k, k1, inds, train_sets, S) == 0.

    assert Pspan(k1, k, inds, train_sets, S) == 0.



    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    assert Pspan(k, k1, inds, train_sets, S) == 1.
    assert Pspan(k1, k, inds, train_sets, S) == 1.


    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 0, 's': 1, 'd': 0})

    assert Pstay(k, k1, inds, train_sets, S) == 1.
    assert Pstay(k1, k, inds, train_sets, S) == 1.


    k = inds.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds.index({'j': 0, 's': 1, 'd': 1})


    assert Pstay(k, k1, inds, train_sets, S) == 0.
    assert Pstay(k1, k, inds, train_sets, S) == 0.

    ### rerouting ####
    train_sets = {
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

    assert P1track(k, k1, inds, train_sets, S) == 1.
    assert P1track(k1, k, inds, train_sets, S) == 1.


    k = inds.index({'j': 1, 's': 0, 'd': 6})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    assert P1track(k, k1, inds, train_sets, S) == 1.
    assert P1track(k1, k, inds, train_sets, S) == 1.

    k = inds.index({'j': 1, 's': 0, 'd': 10})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    assert P1track(k, k1, inds, train_sets, S) == 1.
    assert P1track(k1, k, inds, train_sets, S) == 1.



    k = inds.index({'j': 1, 's': 1, 'd': 1})
    k1 = inds.index({'j': 0, 's': 0, 'd': 2})

    assert P1track(k, k1, inds, train_sets, S) == 0.
    assert P1track(k1, k, inds, train_sets, S) == 0.


    k = inds.index({'j': 1, 's': 1, 'd': 0})
    k1 = inds.index({'j': 2, 's': 1, 'd': 1})

    assert P1track(k, k1, inds, train_sets, S) == 0.
    assert P1track(k1, k, inds, train_sets, S) == 0.




def test_qubic(S, not_considered_station):

    ### rerouting ####
    train_sets = {
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }



    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
    inds_z, l = z_indices(train_sets, S, 10)

    assert l == 121


    inds1 = list(np.concatenate([inds, inds_z]))
    assert len(inds1) == 176

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 1, 'd1': 4})

    assert P1qubic(k, k1, inds1, train_sets, S) == 0.
    assert P1qubic(k1, k, inds1, train_sets, S) == 0.

    #### this should be one #######

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})

    assert P1qubic(k, k1, inds1, train_sets, S) == 1.
    assert P1qubic(k1, k, inds1, train_sets, S) == 1.

    k = inds1.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    assert P1qubic(k, k1, inds1, train_sets, S) == 1.
    assert P1qubic(k1, k, inds1, train_sets, S) == 1.

    ###  P2qubic ####


    k = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 2})

    assert P2qubic(k, k, inds1, train_sets, S) == 3.
    assert P2qubic(k, k1, inds1, train_sets, S) == 0.

    k = inds1.index({'j': 0, 's': 0, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets, S) == 0.

    k = inds1.index({'j': 0, 's': 1, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 10, 'd1': 8})

    assert P2qubic(k, k1, inds1, train_sets, S) == -1.
    assert P2qubic(k1, k, inds1, train_sets, S) == -1.

    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 1, 'd': 0})

    assert P2qubic(k, k1, inds1, train_sets, S) == 0.5
    assert P2qubic(k1, k, inds1, train_sets, S) == 0.5

    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 2, 's': 1, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets, S) == 0.
    assert P2qubic(k1, k, inds1, train_sets, S) == 0.


    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets, S) == 0.
    assert P2qubic(k1, k, inds1, train_sets, S) == 0.


    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


    assert P2qubic(k, k1, inds1, train_sets, S) == 0.
    assert P2qubic(k1, k, inds1, train_sets, S) == 0.



def test_performing_Qmat():
    #####   dispatching problem that was solved on D-Wave   ########

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

    assert np.array_equal(Q, np.load("files/Qfile.npz")["Q"])

    train_sets = {
    "J": [0,1,2],
    "Jd": [],
    "Josingle": [[1,2], []],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }

    Q_r = make_Q(train_sets, S, not_considered_station, 10, p_sum, p_pair, p_pair_qubic, p_qubic)

    assert np.array_equal(Q_r, np.load("files/Qfile_r.npz")["Q"])


test_pspan_pstay_p1track(S, not_considered_station)

test_qubic(S, not_considered_station)

test_performing_Qmat()
