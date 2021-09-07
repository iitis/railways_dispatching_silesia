import sys
sys.path.append('../src')


from helpers_functions import *


def pairs_test():
    assert occurs_as_pair(1,2, [[1,2,3], [4], [5,6]]) == True
    assert occurs_as_pair(2,1, [[1,2,3], [4], [5,6]]) == True
    assert occurs_as_pair(1,4, [[1,2,3], [4], [5,6]]) == False

    d1 = {0: {0:1, 1:2}, 1: {0:1}}
    d2 = {0:{2:3}}
    assert update_dictofdicts(d1, d2) == {0: {0: 1, 1: 2, 2: 3}, 1: {0: 1}}

    d1 = {0: {0:1, 1:2}, 1: {0:1}}
    d2 = {2:{2:3}}
    assert update_dictofdicts(d1, d2) == {0: {0: 1, 1: 2}, 1: {0: 1}, 2: {2:3}}


def trains_paths():

    S = {0: [0,1,2,4], 1: [0,1,2], 2: [1,0]}

    assert previous_station(S, 0, 4) == 2
    assert previous_station(S, 2, 1) == None

    assert subsequent_station(S, 1, 2) == None
    assert subsequent_station(S, 0, 2) == 4
    assert subsequent_station(S, 2, 1) == 0

    assert common_path(S, 0, 1) == [0,1,2]
    assert common_path(S, 0, 2) == [0,1]
    assert common_path(S, 2,1) == [1,0]



def auxiliary_timetable_functions():

    taus = {"pass" : {"0_0_1" : 5, "1_0_1" : 7, "2_1_0" : 10}, "blocks" : {"0_0_1" : 2, "1_0_1" : 3}, "stop": {"0_1_None" : 1, "1_1_None" : 2, "2_0_None" : 1}, "res": 3}
    timetable = {"tau": taus,
                  "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
                  "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}


    assert tau(timetable, "pass", 0, 0, 1) == 5
    assert tau(timetable, "res") == 3

    assert initial_conditions(timetable, 0, 0) == 4
    assert penalty_weights(timetable, 1, 0) == 1
    assert penalty_weights(timetable, 1, 1) == 0
    assert penalty_weights(timetable, 2, 1) == 1

    S = {0: [0,1], 1: [0,1], 2: [1,0]}

    assert earliest_dep_time(S, timetable, 0, 0) == 4
    assert earliest_dep_time(S, timetable, 0, 1) == 10

    assert earliest_dep_time(S, timetable, 2, 0) == 19
    assert earliest_dep_time(S, timetable, 2, 1) == 8

pairs_test()
trains_paths()
auxiliary_timetable_functions()
print("tests done")
