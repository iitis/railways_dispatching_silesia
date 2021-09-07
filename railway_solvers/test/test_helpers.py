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



pairs_test()
trains_paths()
print("tests done")
