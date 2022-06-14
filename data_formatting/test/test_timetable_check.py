import pandas as pd
from data_formatting import get_arrdep, train_time_table, timetable_to_train_dict
from data_formatting import get_arr_dep_vals, train_important_stations, check_path_continuity


def test_timetables():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_path = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    t = get_arrdep(data, 42100) # should return arriving and dep times for blocks where they are given

    timetable_dict = timetable_to_train_dict(data)
    assert timetable_dict[42100][0] == ['IC - IC', 'SZTYGAR', 'from Katowice', 'to Lublin Główny']

    tt = train_time_table(data, 42100)

    assert 'path' in tt
    assert 'speed' in tt
    assert 'Arr' in tt
    assert 'Dep' in tt
    assert 'Approx_enter' in tt
    assert 'Label' in tt
    assert 'Shunting' in tt
    assert 'Turnaround_time_minutes' in tt

    assert tt['speed'][0] == "IC"
    assert tt['speed'][1] == "IC"
    assert tt['speed'][2] == "IC"
    assert tt['Dep'][0] == "16:08"

    adtt = get_arrdep(data, 42100)

    assert 'Arr' in adtt
    assert 'Dep' in adtt
    assert 'Approx_enter' in adtt
    assert adtt["Dep"][0] == "16:08"

    assert get_arr_dep_vals(data, 42100)[0][1] == '16:08'
    assert get_arr_dep_vals(data, 42100)[1][2] == '16:12'
    # others are nan


def test_trains_paths():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_path = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    assert get_arr_dep_vals(data, 42100)[0][1] == '16:08'
    assert get_arr_dep_vals(data, 42100)[1][2] == '16:12'

    assert train_important_stations(data, 42100) == ['KO', 'KO(STM)', 'KZ']

    check_path_continuity(data, data_path.iloc[:,:2], 42100)
