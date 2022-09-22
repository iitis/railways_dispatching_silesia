"""
helpers that concers reading timetable and some primary checks
"""
import pandas as pd
import numpy as np

# convert csv to dictionary
def timetable_to_train_dict(data):
    """
    return a vector of two elements:
    - the notation of particular train [type, name, from to]
    - dict of trains timetable
    keys: 'path', 'speed', 'Arr', 'Dep', 'Approx_enter', 'Label', 'Shunting',
       'Turnaround_time_minutes'
    values are strings or NaN if there is nothing corresponding in csv field
    """
    train_dict = {}
    for i in range(len(data["Unnamed: 0"])):
        if data["Unnamed: 0"][i].isnumeric():
            info = []
            train = int(data["Unnamed: 0"][i])
            info += [data["Unnamed: 0"][i - 1]]
            info += [data["Unnamed: 0"][i + x] for x in range(1, 3)]
        statment = data["Unnamed: 0"][i][0:4]
        if statment in ["from", "depa"]:
            tt_init = i + 1
            tt_item = data["Unnamed: 0"][i + 1]
            pa = 1
            while tt_item[0:2] not in ["to", "te"]:
                pa += 1
                tt_item = data["Unnamed: 0"][i + pa]
            train_data = (
                data.iloc[tt_init : pa - 1 + tt_init]
                .reset_index(drop=True)
                .rename(columns={"Unnamed: 0": "path"})
            )
            info += [data["Unnamed: 0"][pa - 1 + tt_init]]
            train_dict[train] = [info, train_data]
    return train_dict


def train_time_table(train_dict, train):
    """
    return dict of trains timetable
    keys: 'path', 'speed', 'Arr', 'Dep', 'Approx_enter', 'Label', 'Shunting',
       'Turnaround_time_minutes'
    values are strings or NaN if there is nothing corresponding in csv field
    """
    # train_dict = timetable_to_train_dict(data)
    return train_dict[train][1]


def get_arrdep(time_table):
    """ returns arriving, dep, approx dep times for blocks in the form of dict with
    keys: 'Arr', 'Dep', 'Approx_enter'

    Values are strings, if not given in the timetable file they are NaN
    """
    # time_table = train_time_table(data, train)
    arrdep = time_table.loc[:, ["Arr", "Dep", "Approx_enter"]]
    return arrdep


def get_arr_dep_vals(time_table):
    """  return vector of [Arr, Dep, Approx_enter] at stations given in  .csv file
         if filed is empty returns nan
    """
    arrdep = get_arrdep(time_table)
    short_list = arrdep.dropna(how="all")
    arr_dep_vals = []
    for i in range(len(short_list)):
        arr_dep_vals += [short_list.iloc[i].tolist()]
    return arr_dep_vals




def train_important_stations(time_table):
    """  return the vector of important stations of given train """

    filtered_time_table = time_table[time_table['important_station'].notnull()]
    return filtered_time_table["important_station"].values.tolist()


def train_important_stations1(time_table,important_stations):
    """  return the vector of important stations of given train """
    # important_stations = np.load("./important_stations.npz", allow_pickle=True)[
    #     "arr_0"
    # ][()]
    # time_table = train_time_table(data, train)
    blocks = time_table["path"]
    station_list = []
    for block in blocks:
        station_list += [
            key for key, value in important_stations.items() if block in value
        ]
    return station_list


def check_path_continuity(paths, data_path_check):
    """ for given train checks if its path given in data in continious
     with regards to possible paths in data_path_check  if not raise AssertionError
    `not present`
     """
    # paths = train_time_table(data, train)["path"]
    for i in range(len(paths) - 1):
        if data_path_check.isin([paths[i], paths[i + 1]]).all(1).any() == False:
            if data_path_check.isin([paths[i]]).any(1).any() == False:
                raise AssertionError(paths[i], "not present in possible paths")
            if data_path_check.isin([paths[i + 1]]).any(1).any() == False:
                raise AssertionError(paths[i], "not present in possible paths")

