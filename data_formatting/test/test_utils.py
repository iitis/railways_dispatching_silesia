from data_formatting import *

import re
import pandas as pd


def test_helpers():
    list1 = ['a', 'b', 'c']
    list2 = ['b', 'd', 'c']
    assert common_elements(list1, list2) == ['b', 'c']

    list1 = ['a', 'b', 'c']
    list2 = ['c', 'd', 'b']
    assert common_elements(list1, list2) == ['b', 'c']

    t = [['a', 'b'], ['c', 'd']]
    assert flatten(t) == ['a', 'b', 'c', 'd']

    assert getSizeOfNestedList(t) == 4


def test_trains_path():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")

    # vector of all trains
    assert get_J(data) == [94766, 26103, 421009, 42100, 5312, 40518, 34319, 343199, 14006, 94611, 40150, 41004, 94113, 40673, 54101, 541019, 40477, 4500, 94317, 44717, 64350, 94717, 44862, 40628, 40675, 73000, 4120]

    # trains routes determined by stations
    assert get_Paths(data)[94766] == ['Ty', 'KL', 'KO', 'KO(STM)']
    assert get_Paths(data)[26103] == ['KZ', 'KO(STM)', 'KO', 'CB', 'GLC']
    assert get_Paths(data)[421009] == ['KO(IC)', 'KO(STM)', 'KO']

# for train in trains_at_stations[s]:
# get subsequent station for a given train
def test_path_reffering_to_stations():

    path_to_data = "../data/train_schedule.csv"
    data = pd.read_csv(path_to_data, sep = ";")


    train1 = 44717  # goes KL - MJ - Mi
    train2 =  44862  # goes Mi - MJ - Kl

    # common stations of given trains' pair
    assert 'KO(STM)' in check_common_station(data, train1,train2)
    assert 'KO' in check_common_station(data, train1,train2)
    assert 'MJ' in check_common_station(data, train1,train2)
    assert 'Mi' in check_common_station(data, train1,train2)
    assert 'KL' in check_common_station(data, train1,train2)

    # blocks between stations and determine whether trains goes in the same or opposite directions
    # there is one block '"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"' between Mi and MJ
    assert get_blocks_b2win_station4train(data, train1, "MJ", "Mi") == (['"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"'], False)
    assert get_common_blocks_and_direction_b2win_trains(data,train1, train2,"MJ", "Mi") == (['"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"'], 'opposite')

    # trains departuring from particular station
    assert get_trains_at_station(data, True)["Mi"] == [44717, 44862]

    train = 26103
    assert get_Paths(data)[train] == ['KZ', 'KO(STM)', 'KO', 'CB', 'GLC']

    assert is_train_passing_thru_station(data, train, 'KO(STM)') == True
    assert is_train_passing_thru_station(data, train, 'KL') == False
    assert subsequent_station(data, train, 'KO(STM)') == 'KO'
    assert subsequent_station(data, train, 'GLC') == None
    assert get_trains_at_station(data)['CB'] == [26103, 5312, 40150, 40673, 4500, 94317, 64350, 40628, 40675, 73000]
