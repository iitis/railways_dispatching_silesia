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




if True:

    train_sets = {
      "J": [0,1,2],
      "Jd": [[0,1], [2]],
      "Josingle": [],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }


    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
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



if True:

    ### rerouting ####
    train_sets = {
      "J": [0,1,2],
      "Jd": [],
      "Josingle": [[1,2], []],
      "Jround": dict(),
      "Jtrack": {1: [0,1]},
      "Jswitch": dict()
    }


    #### this should be zero #######

    inds, q_bits = indexing4qubo(train_sets, S, 10, not_considered_station)
    inds_z, l = z_indices(train_sets, S, 10)

    print(l == 121)


    inds1 = np.concatenate([inds, inds_z])
    print(len(inds1) == 176)

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
