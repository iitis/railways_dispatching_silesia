import pandas as pd
import numpy as np
from data_formatting import common_elements, flatten, getSizeOfNestedList
from data_formatting import check_common_station, get_blocks_b2win_station4train
from data_formatting import get_common_blocks_and_direction_b2win_trains
from data_formatting import (
    get_trains_at_station,
    get_Paths,
    is_train_passing_thru_station,
)
from data_formatting import subsequent_station, get_trains_at_station
from data_formatting import get_J


from data_formatting import update_all_timetables
from data_formatting import timetable_to_train_dict

data = pd.read_csv("../data/trains_schedules.csv", sep=";")
data_paths = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load("../data/important_stations.npz", allow_pickle=True)[
    "arr_0"
][()]

time_tables_dict = timetable_to_train_dict(data)
train_dict = update_all_timetables(time_tables_dict, data_paths, important_stations)


def test_helpers():
    list1 = ["a", "b", "c"]
    list2 = ["b", "d", "c"]
    assert common_elements(list1, list2) == ["b", "c"]

    list1 = ["a", "b", "c"]
    list2 = ["c", "d", "b"]
    assert common_elements(list1, list2) == ["b", "c"]

    t = [["a", "b"], ["c", "d"]]
    assert flatten(t) == ["a", "b", "c", "d"]

    assert getSizeOfNestedList(t) == 4


def test_helpers4trains_paths():

    train1 = 42100
    train2 = 5312

    assert "KZ" in check_common_station(train_dict, train1, train2)
    assert "KO(STM)" in check_common_station(train_dict, train1, train2)
    assert "KO" in check_common_station(train_dict, train1, train2)


def test_trains_path():

    # vector of all trains
    assert get_J(train_dict) == [
        94766,
        26103,
        421009,
        42100,
        5312,
        40518,
        34319,
        343199,
        14006,
        94611,
        40150,
        41004,
        94113,
        40673,
        54101,
        541019,
        40477,
        4500,
        94317,
        44717,
        64350,
        94717,
        44862,
        40628,
        40675,
        73000,
        4120,
    ]

    # trains routes determined by stations
    assert get_Paths(train_dict)[94766] == ["Ty", "KL", "KO", "KO(STM)"]
    assert get_Paths(train_dict)[26103] == ["KZ", "KO(STM)", "KO", "CB", "GLC"]
    assert get_Paths(train_dict)[421009] == ["KO(IC)", "KO(STM)", "KO"]


# for train in trains_at_stations[s]:
# get subsequent station for a given train


def test_path_reffering_to_stations():

    train1 = 44717  # goes KL - MJ - Mi
    train2 = 44862  # goes Mi - MJ - Kl

    # common stations of given trains' pair
    assert "KO(STM)" in check_common_station(train_dict, train1, train2)
    assert "KO" in check_common_station(train_dict, train1, train2)
    assert "MJ" in check_common_station(train_dict, train1, train2)
    assert "Mi" in check_common_station(train_dict, train1, train2)
    assert "KL" in check_common_station(train_dict, train1, train2)

    # blocks between stations and determine whether trains goes in the same or opposite directions
    # there is one block '"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"' between Mi and MJ
    assert get_blocks_b2win_station4train(train_dict[train1][1], "MJ", "Mi") == (
        ['"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"'],
        False,
    )
    assert get_common_blocks_and_direction_b2win_trains(
        time_tables_dict, train1, train2, "MJ", "Mi"
    ) == (['"MJ-Mi", "Sem(odstep)", 1, "1", "(1)"'], "opposite")

    # trains departuring from particular station
    assert get_trains_at_station(time_tables_dict, important_stations, True)["Mi"] == [
        44717,
        44862,
    ]

    train = 26103
    assert get_Paths(time_tables_dict)[train] == ["KZ", "KO(STM)", "KO", "CB", "GLC"]

    assert is_train_passing_thru_station(time_tables_dict[train][1], "KO(STM)") == True
    assert is_train_passing_thru_station(time_tables_dict[train][1], "KL") == False
    assert subsequent_station(train_dict[train][1], "KO(STM)") == "KO"
    assert subsequent_station(train_dict[train][1], "GLC") == None
    assert get_trains_at_station(train_dict, important_stations)["CB"] == [
        26103,
        5312,
        40150,
        40673,
        4500,
        94317,
        64350,
        40628,
        40675,
        73000,
    ]
