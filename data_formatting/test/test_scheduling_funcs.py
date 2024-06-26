"""
    there should be tests taus
"""
import pandas as pd
import numpy as np
import pytest

from data_formatting import timetable_to_train_dict, update_all_timetables
from data_formatting import (
    get_schedule,
    get_initial_conditions,
    add_delay,
    make_weights,
)

# ---------------- data collections -----------------
data = pd.read_csv("../data/trains_schedules.csv", sep=";")
data_path_check = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load("../data/important_stations.npz", allow_pickle=True)[
    "arr_0"
][()]

time_tables_dict = timetable_to_train_dict(data)
time_tables_dict = update_all_timetables(
    time_tables_dict, data_path_check, important_stations, save=False
)

T1 = "16:00"
# ---------------- data collections -----------------


schedule_t = {
    "94766_Ty": -13,
    "94766_KL": -3,
    "26103_KO": 11,
    "26103_CB": 17,
    "26103_GLC": 36,
    "42100_KO": 8,
    "41004_Ty": 1,
}
schedule = get_schedule(time_tables_dict, T1)


@pytest.mark.parametrize("key, output", list(schedule_t.items()))
def test_schedule(key, output):
    assert schedule[f"{key}"] == output


initial_conditions_t = {
    "94766_Ty": -13,
    "26103_KZ": 0,
    "421009_KO(IC)": -10,
    "42100_KO": 8,
    "5312_GLC": -18,
    "40518_Ty": -9,
    "54101_KZ": 24,
    "541019_KO": 28,
}
initial_conditions = get_initial_conditions(time_tables_dict, T1)


@pytest.mark.parametrize("key, output", list(initial_conditions_t.items()))
def test_initial_conditions(key, output):
    assert initial_conditions[key] == output


test_delay_dict = {
    "94766_Ty": 7,
    "26103_KZ": 0,
    "421009_KO(IC)": -10,
    "42100_KO": 18,
    "5312_GLC": -18,
    "40518_Ty": -9,
}
DELAY = 20
TRAIN = 94766
delayed_dict = add_delay(initial_conditions, TRAIN, DELAY)
DELAY1 = 10
TRAIN1 = 42100
delayed_dict = add_delay(delayed_dict, TRAIN1, DELAY1)


@pytest.mark.parametrize("key, output", list(test_delay_dict.items()))
def test_add_delay_1(key, output):
    assert delayed_dict[key] == output


test_weights_dict = {
    "94766_KO": 1.0,
    "26103_GLC": 1.5,
    "421009_KO(STM)": 0,
    "42100_KZ": 1.5,
    "5312_KZ": 1.5,
    "40518_KO": 1.0,
    "34319_KO(STM)": 1.0,
    "343199_KO": 0.0,
    "14006_Ty": 1.5,
    "94611_Ty": 1.0,
    "40150_KZ": 1.0,
    "41004_KZ": 1.5,
    "94113_Ty": 1.0,
    "40673_CB": 1.0,
    "54101_KO(STM)": 1.5,
    "541019_KO(STM)": 0.0,
    "40477_Ty": 1.0,
    "4500_KZ": 1.75,
    "94317_CM": 1.0,
    "44717_Mi": 1.0,
    "64350_KZ": 1.0,
    "94717_Ty": 1.0,
    "44862_KO": 1.0,
    "40628_KZ": 1.0,
    "40675_CB": 1.0,
    "73000_KZ": 1.5,
    "4120_KZ": 1.5,
}

skip_stations = {
    94766: "KO(STM)",
    421009: "KO",
    40518: "KO(STM)",
    34319: "KO",
    343199: "KO(STM)",
    40673: "GLC",
    54101: "KO",
    541019: "KO(IC)",
    44862: "KO(STM)",
    40675: "GLC",
}

penalty_weights = make_weights(
    time_tables_dict, skip_stations, stopping=1, fast=1.5, express=1.75, empty=0
)


@pytest.mark.parametrize("key, output", list(test_weights_dict.items()))
def test_penalty_weights(key, output):
    assert penalty_weights[key] == output
