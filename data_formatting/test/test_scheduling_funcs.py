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
data = pd.read_csv("../data/train_schedule.csv", sep=";")
data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
important_stations = np.load("./important_stations.npz", allow_pickle=True)["arr_0"][()]

time_tables_dict = timetable_to_train_dict(data)
time_tables_dict = update_all_timetables(
    time_tables_dict, data_path_check, important_stations, save=False
)

t1 = "16:00"
# ---------------- data collections -----------------


test_schedule = {
    "94766_Ty": -13,
    "94766_KL": -3,
    "26103_KO": 11,
    "26103_CB": 17,
    "26103_GLC": 36,
    "42100_KO": 8,
    "41004_Ty": 1,
}
schedule = get_schedule(time_tables_dict, t1)


@pytest.mark.parametrize("key, output", list(test_schedule.items()))
def test_schedule(key, output):
    assert schedule[f"{key}"] == output


test_initial_conditions = {
    "94766_Ty": -13,
    "26103_KZ": 0,
    "421009_KO(IC)": -10,
    "42100_KO": 8,
    "5312_GLC": -18,
    "40518_Ty": -9,
    "54101_KZ": 24,
    "541019_KO": 28,
}
initial_conditions = get_initial_conditions(time_tables_dict, t1)


@pytest.mark.parametrize("key, output", list(test_initial_conditions.items()))
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
delay = 20
train = 94766
delayed_dict = add_delay(initial_conditions, train, delay)
delay1 = 10
train1 = 42100
delayed_dict = add_delay(delayed_dict, train1, delay1)


@pytest.mark.parametrize("key, output", list(test_delay_dict.items()))
def test_add_delay_1(key, output):
    assert delayed_dict[key] == output


test_weights_dict = {
    "94766_KO": 1.0,
    "26103_CB": 1.5,
    "421009_KO(STM)": 0,
    "42100_KO(STM)": 1.5,
    "5312_KO(STM)": 1.5,
    "40518_KO": 1.0,
    "34319_KO(STM)": 1.0,
    "343199_KO": 0.0,
    "14006_KL": 1.5,
    "94611_KL": 1.0,
    "40150_KO(STM)": 1.0,
    "14006_KL": 1.5,
    "94113_KL": 1.0,
    "40673_CB": 1.0,
    "54101_KO(STM)": 1.5,
    "541019_KO(STM)": 0.0,
    "40477_KL": 1.0,
    "4500_KO(STM)": 1.75,
}
penalty_weights = make_weights(
    time_tables_dict, stopping=1, fast=1.5, express=1.75, empty=0
)


@pytest.mark.parametrize("key, output", list(test_weights_dict.items()))
def test_penalty_weights(key, output):
    assert penalty_weights[key] == output
