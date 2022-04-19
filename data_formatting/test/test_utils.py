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




# for train in trains_at_stations[s]:
# get subsequent station for a given train
def station_path_test(data):

    train = 26103
    assert get_Paths(data)[train] == ['KZ', 'KO(STM)', 'KO', 'CB', 'GLC']

    assert is_train_passing_thru_station(data, train, 'KO(STM)') == True
    assert is_train_passing_thru_station(data, train, 'KL') == False
    assert subsequent_station(data, train, 'KO(STM)') == 'KO'
    assert subsequent_station(data, train, 'GLC') == None
    assert get_trains_at_station(data)['CB'] == [26103, 5312, 40150, 40673, 4500, 94317, 64350, 40628, 40675, 73000]


path_to_data = "../data/train_schedule.csv"
data = pd.read_csv(path_to_data, sep = ";")
test_helpers()
station_path_test(data)
