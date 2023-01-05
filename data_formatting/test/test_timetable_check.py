import pandas as pd
import numpy as np
from data_formatting import get_arrdep, train_time_table, timetable_to_train_dict
from data_formatting import (
    get_arr_dep_vals,
    train_important_stations,
    check_path_continuity,
)

from data_formatting import update_all_timetables
from data_formatting import timetable_to_train_dict

data = pd.read_csv("../data/trains_schedules.csv", sep=";")
data_paths = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load("../data/important_stations.npz", allow_pickle=True)[
    "arr_0"
][()]

time_tables_dict = timetable_to_train_dict(data)
train_dict = update_all_timetables(time_tables_dict, data_paths, important_stations)


def test_timetables():

    t = get_arrdep(
        train_dict[42100][1]
    )  # should return arriving and dep times for blocks where they are given

    timetable_dict = timetable_to_train_dict(data)
    assert timetable_dict[42100][0] == [
        "IC - IC",
        "SZTYGAR",
        "from Katowice",
        "to Lublin Główny",
    ]

    tt = train_time_table(timetable_dict, 42100)

    assert "path" in tt
    assert "speed" in tt
    assert "Arr" in tt
    assert "Dep" in tt
    assert "Approx_enter" in tt
    assert "Label" in tt
    assert "Shunting" in tt
    assert "Turnaround_time_minutes" in tt

    assert tt["speed"][0] == "IC"
    assert tt["speed"][1] == "IC"
    assert tt["speed"][2] == "IC"
    assert tt["Dep"][0] == "16:08"

    adtt = get_arrdep(train_dict[42100][1])

    assert "Arr" in adtt
    assert "Dep" in adtt
    assert "Approx_enter" in adtt
    assert adtt["Dep"][0] == "16:08"

    assert get_arr_dep_vals(train_dict[42100][1])[0][1] == "16:08"
    assert get_arr_dep_vals(train_dict[42100][1])[1][2] == "16:12"
    # others are nan


def test_trains_paths():
    paths = train_time_table(train_dict, 42100)["path"]

    assert get_arr_dep_vals(train_dict[42100][1])[0][1] == "16:08"
    assert get_arr_dep_vals(train_dict[42100][1])[1][2] == "16:12"

    assert train_important_stations(train_dict[42100][1]) == ["KO", "KO(STM)", "KZ"]

    check_path_continuity(paths, data_paths.iloc[:, :2])
