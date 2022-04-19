from data_formatting import *
import pandas as pd
from tkinter.tix import Tree

def test_helpers():

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_switch = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    # vector of all trains
    assert get_J(data) == [94766, 26103, 421009, 42100, 5312, 40518, 34319, 343199, 14006, 94611, 40150, 41004, 94113, 40673, 54101, 541019, 40477, 4500, 94317, 44717, 64350, 94717, 44862, 40628, 40675, 73000, 4120]

    # trains routes determined by stations
    assert get_Paths(data)[94766] == ['Ty', 'KL', 'KO', 'KO(STM)']
    assert get_Paths(data)[26103] == ['KZ', 'KO(STM)', 'KO', 'CB', 'GLC']
    assert get_Paths(data)[421009] == ['KO(IC)', 'KO(STM)', 'KO']


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

    print("helpers tested")


def test_Js():

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_switch = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    #######    particulat Js #####

    # rolling stock circulation J
    assert get_jround(data) == {'KO': [[421009, 42100], [34319, 343199], [54101, 541019]]}

    # single track occupation
    assert josingle(data, ["CM", "CB"]) == {}
    assert josingle(data, ["Mi", "MJ"]) == {('Mi', 'MJ'): [[44862, 44717]]}

    assert josingle(data, ['KL', 'MJ', 'Mi']) == {('KL', 'MJ'): [[44717, 44862]], ('MJ', 'Mi'): [[44717, 44862]]}

    assert josingle(data, ['GLC', 'CB']) ==  {}

    assert josingle(data, ['CM', 'CB']) ==  {}
    # specific dict format

    trains_same_station_block = jtrack(data)
    assert trains_same_station_block["KZ"] == [[26103, 14006, 40673, 54101, 40675], [42100, 40150, 41004, 4500, 40628, 4120], [5312, 64350, 73000], [34319, 94317]]
    assert trains_same_station_block["KO"] == [[94766, 40518, 34319, 343199, 64350, 44862], [26103, 40673, 40477, 94317], [421009, 42100, 4500, 40628], [5312, 40150, 73000], [14006, 54101, 541019, 40675], [94611, 94113, 44717, 94717], [41004, 4120]]
    assert trains_same_station_block["KO(STM)"] == [[26103, 14006, 40673, 54101, 40675], [421009, 42100, 5312, 34319, 40150, 4500, 40628, 73000, 4120], [41004, 64350], [541019, 94317]]
    assert trains_same_station_block["CB"] == [[26103, 40673, 40675], [5312, 40150, 4500, 40628, 73000], [94317], [64350]]
    assert trains_same_station_block["GLC"] == [[26103], [5312], [40150, 40673, 40628, 40675], [4500], [73000]]
    assert trains_same_station_block["KL"] == [[94766, 40518, 41004, 44862, 4120], [14006, 94611, 94113, 40477, 94717], [44717]]
    assert trains_same_station_block["Mi"] == [[44717], [44862]]
    assert trains_same_station_block["MJ"] == [[44717], [44862]]
    assert trains_same_station_block["CM"] == [[94317], [64350]]

    switches = jswitch(data, data_switch, ["GLC", "MJ", "Mi", "CB", "KO(IC)", "KO(KS)"])

    assert switches["GLC"] == [{26103: 'in', 40673: 'in'}, {26103: 'in', 40675: 'in'}, {5312: 'out', 40150: 'out'}, {5312: 'out', 4500: 'out'}, {5312: 'out', 40628: 'out'}, {5312: 'out', 73000: 'out'}, {40150: 'out', 4500: 'out'}, {40150: 'out', 40628: 'out'}, {40150: 'out', 73000: 'out'}, {40673: 'in', 40675: 'in'}, {4500: 'out', 40628: 'out'}, {4500: 'out', 73000: 'out'}, {40628: 'out', 73000: 'out'}]

    assert switches['MJ'] == [{44717: 'in', 44862: 'out'}, {44717: 'out', 44862: 'in'}]

    assert switches['Mi'] == [{44717: 'in', 44862: 'out'}]

    assert switches['CB'] == [{26103: 'in', 40673: 'in'}, {26103: 'out', 40673: 'out'}, {26103: 'in', 94317: 'in'}, {26103: 'in', 40675: 'in'}, {26103: 'out', 40675: 'out'}, {5312: 'in', 40150: 'in'}, {5312: 'out', 40150: 'out'}, {5312: 'in', 4500: 'in'}, {5312: 'out', 4500: 'out'}, {5312: 'out', 94317: 'in'}, {5312: 'out', 64350: 'out'}, {5312: 'in', 40628: 'in'}, {5312: 'out', 40628: 'out'}, {5312: 'in', 73000: 'in'}, {5312: 'out', 73000: 'out'}, {40150: 'in', 4500: 'in'}, {40150: 'out', 4500: 'out'}, {40150: 'out', 94317: 'in'}, {40150: 'out', 64350: 'out'}, {40150: 'in', 40628: 'in'}, {40150: 'out', 40628: 'out'}, {40150: 'in', 73000: 'in'}, {40150: 'out', 73000: 'out'}, {40673: 'in', 94317: 'in'}, {40673: 'in', 40675: 'in'}, {40673: 'out', 40675: 'out'}, {4500: 'out', 94317: 'in'}, {4500: 'out', 64350: 'out'}, {4500: 'in', 40628: 'in'}, {4500: 'out', 40628: 'out'}, {4500: 'in', 73000: 'in'}, {4500: 'out', 73000: 'out'}, {94317: 'in', 40628: 'out'}, {94317: 'in', 40675: 'in'}, {94317: 'in', 73000: 'out'}, {64350: 'out', 40628: 'out'}, {64350: 'out', 73000: 'out'}, {40628: 'in', 73000: 'in'}, {40628: 'out', 73000: 'out'}]

    assert switches['KO(IC)'] == []

    assert switches['KO(KS)'] == []

    print("trains sets tested")

    ####   Jd   have to be encoded   ########




test_helpers()
test_Js()
