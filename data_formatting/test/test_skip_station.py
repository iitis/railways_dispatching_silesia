"""
    there should be tests taus
"""
import pandas as pd
import numpy as np
import pytest
from data_formatting import timetable_to_train_dict, update_all_timetables
from data_formatting import get_skip_stations


data = pd.read_csv("../data/trains_schedules.csv", sep=";")
data_path_check = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load("../data/important_stations.npz", allow_pickle=True)[
    "arr_0"
][()]

time_tables_dict = timetable_to_train_dict(data)
time_tables_dict = update_all_timetables(
    time_tables_dict, data_path_check, important_stations, save=False
)


skip_station_sample = {
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

skip_station = get_skip_stations(time_tables_dict)


@pytest.mark.parametrize("key, output", list(skip_station_sample.items()))
def test_skip_station(key, output):
    assert skip_station[key] == output
