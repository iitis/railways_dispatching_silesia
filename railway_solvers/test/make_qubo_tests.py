import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
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

train_sets = {
  "J": [0,1,2],
  "Jd": [[0,1], [2]],
  "Josingle": [],
  "Jround": dict(),
  "Jtrack": {1: [0,1]},
  "Jswitch": dict()
}

inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)

if True:

    ### should be zero

    k = inds.index({'j': 0, 's': 0, 'd': 3})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    print(Pspan(k, k1, inds, train_sets, S) == 0.)

    print(Pspan(k1, k, inds, train_sets, S) == 0.)


    ### should be one

    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 1, 's': 0, 'd': 0})

    print(Pspan(k, k1, inds, train_sets, S) == 1.)
    print(Pspan(k1, k, inds, train_sets, S) == 1.)


    ### should be one ###

    k = inds.index({'j': 0, 's': 0, 'd': 2})
    k1 = inds.index({'j': 0, 's': 1, 'd': 0})

    print(Pstay(k, k1, inds, train_sets, S) == 1.)
    print(Pstay(k1, k, inds, train_sets, S) == 1.)


    k = inds.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds.index({'j': 0, 's': 1, 'd': 1})

    ### should be zero ###
    #print(inds[1])
    #print(inds[12])


    print(Pstay(k, k1, inds, train_sets, S) == 0.)
    print(Pstay(k1, k, inds, train_sets, S) == 0.)

### rerouting ####
train_sets = {
  "J": [0,1,2],
  "Jd": [],
  "Josingle": [[1,2], []],
  "Jround": dict(),
  "Jtrack": {1: [0,1]},
  "Jswitch": dict()
}


if True:



    #### this should be zero #######

    ### .....  1 track  ......


    k = inds.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    print(P1track(k, k1, inds, train_sets, S) == 1.)
    print(P1track(k1, k, inds, train_sets, S) == 1.)


    k = inds.index({'j': 1, 's': 0, 'd': 6})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    print(P1track(k, k1, inds, train_sets, S) == 1.)
    print(P1track(k1, k, inds, train_sets, S) == 1.)

    k = inds.index({'j': 1, 's': 0, 'd': 10})
    k1 = inds.index({'j': 2, 's': 1, 'd': 0})

    print(P1track(k, k1, inds, train_sets, S) == 1.)
    print(P1track(k1, k, inds, train_sets, S) == 1.)


    ### should be 0  ####


    k = inds.index({'j': 1, 's': 1, 'd': 1})
    k1 = inds.index({'j': 0, 's': 0, 'd': 2})

    print(P1track(k, k1, inds, train_sets, S) == 0.)
    print(P1track(k1, k, inds, train_sets, S) == 0.)


    k = inds.index({'j': 1, 's': 1, 'd': 0})
    k1 = inds.index({'j': 2, 's': 1, 'd': 1})

    print(P1track(k, k1, inds, train_sets, S) == 0.)
    print(P1track(k1, k, inds, train_sets, S) == 0.)


inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
inds_z, l = z_indices(train_sets, S, 10)

print(l == 121)


inds1 = list(np.concatenate([inds, inds_z]))
print(len(inds1) == 176)


if True:

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 1, 'd1': 4})

    print(P1qubic(k, k1, inds1, train_sets, S) == 0.)
    print(P1qubic(k1, k, inds1, train_sets, S) == 0.)

    #### this should be one #######

    k = inds1.index({'j': 0, 's': 0, 'd': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})

    print(P1qubic(k, k1, inds1, train_sets, S) == 1.)
    print(P1qubic(k1, k, inds1, train_sets, S) == 1.)

    k = inds1.index({'j': 1, 's': 0, 'd': 0})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    print(P1qubic(k, k1, inds1, train_sets, S) == 1.)
    print(P1qubic(k1, k, inds1, train_sets, S) == 1.)

    ###  P2qubic ####


    k = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 1})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 2})

    print(P2qubic(k, k, inds1, train_sets, S) == 3.)
    print(P2qubic(k, k1, inds1, train_sets, S) == 0.)

    k = inds1.index({'j': 0, 's': 0, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 4, 'd1': 8})

    print(P2qubic(k, k1, inds1, train_sets, S) == 0.)

    k = inds1.index({'j': 0, 's': 1, 'd': 10})
    k1 = inds1.index({'j': 0, 'j1': 1, 's': 1, 'd': 10, 'd1': 8})

    print(P2qubic(k, k1, inds1, train_sets, S) == -1.)
    print(P2qubic(k1, k, inds1, train_sets, S) == -1.)

    k = inds1.index({'j': 0, 's': 1, 'd': 1})
    k1 = inds1.index({'j': 1, 's': 1, 'd': 0})

    print(P2qubic(k, k1, inds1, train_sets, S) == 0.5)
    print(P2qubic(k1, k, inds1, train_sets, S) == 0.5)

k = inds1.index({'j': 0, 's': 1, 'd': 1})
k1 = inds1.index({'j': 2, 's': 1, 'd': 0})


print(P2qubic(k, k1, inds1, train_sets, S) == 0.)
print(P2qubic(k1, k, inds1, train_sets, S) == 0.)


k = inds1.index({'j': 0, 's': 0, 'd': 1})
k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


print(P2qubic(k, k1, inds1, train_sets, S) == 0.)
print(P2qubic(k1, k, inds1, train_sets, S) == 0.)


k = inds1.index({'j': 0, 's': 1, 'd': 1})
k1 = inds1.index({'j': 1, 's': 0, 'd': 0})


print(P2qubic(k, k1, inds1, train_sets, S) == 0.)
print(P2qubic(k1, k, inds1, train_sets, S) == 0.)


Q = np.load("files/Qfile.npz")["Q"]

Q_r = np.load("files/Qfile_r.npz")["Q"]


print(Q)

print(Q_r)
