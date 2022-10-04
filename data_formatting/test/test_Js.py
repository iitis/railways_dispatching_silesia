import pandas as pd
import numpy as np
from data_formatting import get_trains_pair9, get_jround, josingle, jswitch, jtrack
from data_formatting import jd
from data_formatting import update_all_timetables
from data_formatting import timetable_to_train_dict

data = pd.read_csv("../data/train_schedule.csv", sep = ";")
data_paths = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]

time_tables_dict = timetable_to_train_dict(data)
train_dict = update_all_timetables(time_tables_dict,data_paths,important_stations)


def test_Js():

    #######    particulat Js #####

    # rolling stock circulation J
    # helper
    assert get_trains_pair9(train_dict) == [[42100, 421009], [34319, 343199], [54101, 541019]]
    # main function
    assert get_jround(train_dict,important_stations) == {'KO': [[421009, 42100], [34319, 343199], [54101, 541019]]}


def test_josingle():

    # single track occupation
    assert josingle(train_dict,important_stations,["CM", "CB"]) == {}
    assert josingle(train_dict,important_stations,["Mi", "MJ"]) == {('Mi', 'MJ'): [[44862, 44717]]}

    assert josingle(train_dict,important_stations,['KL', 'MJ', 'Mi']) == {('KL', 'MJ'): [[44717, 44862]], ('MJ', 'Mi'): [[44717, 44862]]}

    assert josingle(train_dict,important_stations,['GLC', 'CB']) ==  {}

    assert josingle(train_dict,important_stations,['CM', 'CB']) ==  {}
    # specific dict format

    trains_same_station_block = jtrack(train_dict,important_stations)
    assert trains_same_station_block["KZ"] == [[26103, 14006, 40673, 54101, 40675], [42100, 40150, 41004, 4500, 40628, 4120], [5312, 64350, 73000], [34319, 94317]]
    assert trains_same_station_block["KO"] == [[94766, 40518, 34319, 343199, 64350, 44862], [26103, 40673, 40477, 94317], [421009, 42100, 4500, 40628], [5312, 40150, 73000], [14006, 54101, 541019, 40675], [94611, 94113, 44717, 94717], [41004, 4120]]
    assert trains_same_station_block["KO(STM)"] == [[26103, 14006, 40673, 54101, 40675], [421009, 42100, 5312, 34319, 40150, 4500, 40628, 73000, 4120], [41004, 64350], [541019, 94317]]
    assert trains_same_station_block["CB"] == [[26103, 40673, 40675], [5312, 40150, 4500, 40628, 73000], [94317], [64350]]
    assert trains_same_station_block["GLC"] == [[26103], [5312], [40150, 40673, 40628, 40675], [4500], [73000]]
    assert trains_same_station_block["KL"] == [[94766, 40518, 41004, 44862, 4120], [14006, 94611, 94113, 40477, 94717], [44717]]
    assert trains_same_station_block["Mi"] == [[44717], [44862]]
    assert trains_same_station_block["MJ"] == [[44717], [44862]]
    assert trains_same_station_block["CM"] == [[94317], [64350]]


def test_Jswitches():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_switch = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    switches = jswitch(data, data_switch, ["GLC", "MJ", "Mi", "CB", "KO(IC)", "KO(KS)"])

    assert switches["GLC"] == [{26103: 'in', 40673: 'in'}, {26103: 'in', 40675: 'in'}, {5312: 'out', 40150: 'out'}, {5312: 'out', 4500: 'out'}, {5312: 'out', 40628: 'out'}, {5312: 'out', 73000: 'out'}, {40150: 'out', 4500: 'out'}, {40150: 'out', 40628: 'out'}, {40150: 'out', 73000: 'out'}, {40673: 'in', 40675: 'in'}, {4500: 'out', 40628: 'out'}, {4500: 'out', 73000: 'out'}, {40628: 'out', 73000: 'out'}]

    assert switches['MJ'] == [{44717: 'in', 44862: 'out'}, {44717: 'out', 44862: 'in'}]

    assert switches['Mi'] == [{44717: 'in', 44862: 'out'}]

    assert switches['CB'] == [{26103: 'in', 40673: 'in'}, {26103: 'out', 40673: 'out'}, {26103: 'in', 94317: 'in'}, {26103: 'in', 40675: 'in'}, {26103: 'out', 40675: 'out'}, {5312: 'in', 40150: 'in'}, {5312: 'out', 40150: 'out'}, {5312: 'in', 4500: 'in'}, {5312: 'out', 4500: 'out'}, {5312: 'out', 94317: 'in'}, {5312: 'out', 64350: 'out'}, {5312: 'in', 40628: 'in'}, {5312: 'out', 40628: 'out'}, {5312: 'in', 73000: 'in'}, {5312: 'out', 73000: 'out'}, {40150: 'in', 4500: 'in'}, {40150: 'out', 4500: 'out'}, {40150: 'out', 94317: 'in'}, {40150: 'out', 64350: 'out'}, {40150: 'in', 40628: 'in'}, {40150: 'out', 40628: 'out'}, {40150: 'in', 73000: 'in'}, {40150: 'out', 73000: 'out'}, {40673: 'in', 94317: 'in'}, {40673: 'in', 40675: 'in'}, {40673: 'out', 40675: 'out'}, {4500: 'out', 94317: 'in'}, {4500: 'out', 64350: 'out'}, {4500: 'in', 40628: 'in'}, {4500: 'out', 40628: 'out'}, {4500: 'in', 73000: 'in'}, {4500: 'out', 73000: 'out'}, {94317: 'in', 40628: 'out'}, {94317: 'in', 40675: 'in'}, {94317: 'in', 73000: 'out'}, {64350: 'out', 40628: 'out'}, {64350: 'out', 73000: 'out'}, {40628: 'in', 73000: 'in'}, {40628: 'out', 73000: 'out'}]

    assert switches['KO(IC)'] == []

    assert switches['KO(KS)'] == []

    print("trains sets tested")

def test_Jd():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")

    # testing particular stations = fast
    Jd_s = jd(data, ["GLC", "MJ", "KZ"])
    assert Jd_s["GLC"]["CB"] == [[5312, 40150, 4500, 40628, 73000]]
    assert Jd_s["MJ"]["KL"] == [[44862]]
    assert Jd_s["MJ"]["Mi"] == [[44717]]
    assert Jd_s["KZ"]["KO(STM)"] == [[26103, 14006, 40673, 54101, 40675], [34319, 94317]]

    # testing all, slow
    Jd_all = jd(data)
    assert Jd_all["KO"]["CB"] == [[26103, 40673, 94317, 40675]]
    assert Jd_all["KO"]["KL"] == [[14006, 94611, 94113, 40477, 44717, 94717]]
    assert Jd_all["KO"]["KO(STM)"] == [[94766, 42100, 5312, 40518, 343199, 40150, 41004, 541019, 4500, 64350, 44862, 40628, 73000, 4120]]
    assert Jd_all["KO(KS)"]["KO"] == [[94611, 94113]]
    assert Jd_all["KO(STM)"]["KO(IC)"] == [[541019]]
    assert Jd_all["KO(IC)"]["KO(STM)"] == [[421009]]
