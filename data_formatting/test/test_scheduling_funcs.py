"""
    there sholud be tests taus
"""
import pandas as pd
import numpy as np
import pytest
from data_formatting import get_taus_pass, get_taus_stop, get_taus_prep, get_taus_headway
from data_formatting import timetable_to_train_dict, update_all_timetables
from data_formatting import get_schedule, get_initial_conditions, add_delay

# ---------------- data coletions -----------------
data = pd.read_csv("../data/train_schedule.csv", sep = ";")
data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]

time_tables_dict = timetable_to_train_dict(data)
time_tables_dict = update_all_timetables(time_tables_dict,data_path_check,important_stations,save = False)

t1 = '16:00'
delay= 20
train = 94766
# ---------------- data coletions -----------------


test_schedule = {"94766_Ty": -13, "94766_KL": -3, "26103_KO": 11, "26103_CB": 17, "26103_GLC": 36, "42100_KO": 8}
schedule = get_schedule(time_tables_dict,t1)

@pytest.mark.parametrize("key, output",list(test_schedule.items()))
def test_schedule(key,output):
    assert schedule[f"{key}"] == output


test_itial_conditions =  {"94766_Ty": -13, "26103_KZ": 0, "421009_KO(IC)": -10, "42100_KO": 8, "5312_GLC": -18, "40518_Ty": -9}
initial_conditions = get_initial_conditions(time_tables_dict,t1)

@pytest.mark.parametrize("key, output",list(test_itial_conditions.items()))
def test_initial_conditions(key,output):
    assert initial_conditions[key]==output


test_add_delay = {"94766_Ty": 7, "26103_KZ": 0, "421009_KO(IC)": -10, "42100_KO": 8, "5312_GLC": -18, "40518_Ty": -9}
delayed_dict = add_delay(initial_conditions,train,delay)

@pytest.mark.parametrize("key, output",list(test_add_delay.items()))
def test_add_delay(key,output):
    assert delayed_dict[key] == output
