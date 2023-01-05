"""
    there should be tests taus
"""
import pandas as pd
import numpy as np
import pytest
from data_formatting import (
    get_taus_pass,
    get_taus_stop,
    get_taus_prep,
    get_taus_headway,
)
from data_formatting import timetable_to_train_dict, update_all_timetables

data = pd.read_csv("../data/trains_schedules.csv", sep=";")
data_path_check = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load("../data/important_stations.npz", allow_pickle=True)[
    "arr_0"
][()]

time_tables_dict = timetable_to_train_dict(data)
time_tables_dict = update_all_timetables(
    time_tables_dict, data_path_check, important_stations, save=False
)


test_pass = {
    "94766_Ty_KL": 8,
    "94766_KL_KO": 5,
    "94766_KO_KO(STM)": 0,
    "26103_KZ_KO(STM)": 1,
    "26103_KO(STM)_KO": 0,
    "26103_KO_CB": 3,
    "26103_CB_GLC": 14,
    "421009_KO(IC)_KO(STM)": 0,
    "421009_KO(STM)_KO": 0,
    "42100_KO_KO(STM)": 0,
    "42100_KO(STM)_KZ": 1,
}

taus_pass = get_taus_pass(time_tables_dict)


@pytest.mark.parametrize("key, output", list(test_pass.items()))
def test_taus_pass(key, output):
    assert taus_pass[f"{key}"] == output


test_pass_not_round = {
    "94766_Ty_KL": pytest.approx(7.8),
    "42100_KO_KO(STM)": pytest.approx(0),
    "42100_KO(STM)_KZ": pytest.approx(1.3),
}

taus_pass_not_round = get_taus_pass(time_tables_dict, r=0)


@pytest.mark.parametrize("key, output", list(test_pass_not_round.items()))
def test_taus_pass_not_round(key, output):
    assert taus_pass_not_round[f"{key}"] == output


test_stop = {
    "94766_Ty": 2,
    "94766_KL": 1,
    "94766_KO": 3,
    "26103_KZ": 1,
    "26103_KO(STM)": 2,
    "26103_KO": 3,
    "26103_CB": 2,
    "26103_GLC": 1,
    "421009_KO(STM)": 2,
    "42100_KO": 3,
    "42100_KO(STM)": 1,
    "42100_KZ": 1,
}

taus_stop, _ = get_taus_stop(time_tables_dict, important_stations)


@pytest.mark.parametrize("key, output", list(test_stop.items()))
def test_taus_stop(key, output):
    assert taus_stop[key] == output


test_stop_not_round = {
    "26103_KO(STM)": pytest.approx(1.7),
    "421009_KO(STM)": pytest.approx(1.7),
    "42100_KO": pytest.approx(3),
}

taus_stop_not_round, _ = get_taus_stop(time_tables_dict, important_stations, r=0)


@pytest.mark.parametrize("key, output", list(test_stop_not_round.items()))
def test_taus_stop(key, output):
    assert taus_stop_not_round[key] == output


def test_taus_prep():
    prep = {"42100_KO": 5, "343199_KO": 5, "541019_KO": 5}
    taus_prep = get_taus_prep(time_tables_dict, important_stations, r=0)
    assert taus_prep == prep


test_headway = {
    "26103_14006_KZ_KO(STM)": 1,
    "26103_40673_KZ_KO(STM)": 1,
    "26103_54101_KZ_KO(STM)": 1,
    "26103_40675_KZ_KO(STM)": 1,
    "14006_40673_KZ_KO(STM)": 1,
    "14006_54101_KZ_KO(STM)": 1,
    "14006_40675_KZ_KO(STM)": 1.0,
    "94766_40518_Ty_KL": 2.0,
    "40518_94766_Ty_KL": 2.0,
    "94766_41004_Ty_KL": 4.0,
    "41004_94766_Ty_KL": 2.0,
}


taus_headway = get_taus_headway(time_tables_dict, important_stations)


@pytest.mark.parametrize("key, output", list(test_headway.items()))
def test_taus_headway(key, output):
    assert taus_headway[f"{key}"] == output


test_headway_not_round = {
    "26103_14006_KZ_KO(STM)": pytest.approx(1.2),
    "26103_40673_KZ_KO(STM)": pytest.approx(1.2),
    "94766_40518_Ty_KL": pytest.approx(2.5),
    "40518_94766_Ty_KL": pytest.approx(2.5),
    "94766_41004_Ty_KL": pytest.approx(3.8),
    "41004_94766_Ty_KL": pytest.approx(1.7),
}


taus_headway_not_round = get_taus_headway(time_tables_dict, important_stations, r=0)


@pytest.mark.parametrize("key, output", list(test_headway_not_round.items()))
def test_taus_headway(key, output):
    assert taus_headway_not_round[f"{key}"] == output
