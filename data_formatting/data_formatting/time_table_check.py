"""
helpers that concers reading timetable and some primary checks
"""
import pandas as pd
import numpy as np

# from data_formatting.utils import  get_blocks_b2win_station4train
# from data_formatting.print_timetable import get_indexes, get_path_type_colunm


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


def train_time_table(data, train):
    """
    return dict of trains timetable
    keys: 'path', 'speed', 'Arr', 'Dep', 'Approx_enter', 'Label', 'Shunting',
       'Turnaround_time_minutes'
    values are strings or NaN if there is nothing corresponding in csv field
    """
    train_dict = timetable_to_train_dict(data)
    time_table = train_dict[train][1]
    return time_table


def get_arrdep(data, train):
    """ returns arriving, dep, approx dep times for blocks in the form of dict with
    keys: 'Arr', 'Dep', 'Approx_enter'

    Values are strings, if not given in the timetable file they are NaN
    """
    time_table = train_time_table(data, train)
    arrdep = time_table.loc[:, ["Arr", "Dep", "Approx_enter"]]
    return arrdep


def get_arr_dep_vals(data, train):
    """  return vector of [Arr, Dep, Approx_enter] at stations given in  .csv file
         if filed is empty returns nan
    """
    arrdep = get_arrdep(data, train)
    short_list = arrdep.dropna(how="all")
    arr_dep_vals = []
    for i in range(len(short_list)):
        arr_dep_vals += [short_list.iloc[i].tolist()]
    return arr_dep_vals


def train_important_stations(data, train):
    """  return the vector of important stations of given train """
    important_stations = np.load("./important_stations.npz", allow_pickle=True)[
        "arr_0"
    ][()]
    time_table = train_time_table(data, train)
    blocks = time_table["path"]
    station_list = []
    for block in blocks:
        station_list += [
            key for key, value in important_stations.items() if block in value
        ]
    return station_list


def check_path_continuity(data, data_path_check, train):
    """ for given train checks if its path given in data in continious
     with regards to possible paths in data_path_check  if not raise AssertionError
    `not present`
     """
    paths = train_time_table(data, train)["path"]
    for i in range(len(paths) - 1):
        if data_path_check.isin([paths[i], paths[i + 1]]).all(1).any() == False:
            if data_path_check.isin([paths[i]]).any(1).any() == False:
                raise AssertionError(paths[i], "not present in possible paths")
            if data_path_check.isin([paths[i + 1]]).any(1).any() == False:
                raise AssertionError(paths[i], "not present in possible paths")


def get_passing_time_4blocks(blocks_list,block_speed_list,data_path_check):
    assert len(blocks_list) > 1, "only one block? can't continue"
    time = 0
    for i in range(len(blocks_list)-1):
        value1,value2 = blocks_list[i:i+2]
        v1_speed = block_speed_list[i]
        data_check = data_path_check.loc[data_path_check["previous_block"].isin([value1,value2]) & data_path_check["next_block"].isin([value1,value2])]
        assert data_check.empty == False, "this combination is not valid"
        block_dir = get_indexes(data_check,value1)[0][1]
        speed_path = get_path_type_colunm(v1_speed,block_dir)
        time += float(data_check.iloc[0][speed_path])
        print(time)
    return time

def minimal_passing_time(train,station1,station2,data,data_path_check,resolution=1):
    assert train in get_J(data),"train does not exist"
    assert station1 and station2 in train_important_stations(data, train)
    blocks,_,bl_speed = get_blocks_b2win_station4train(data, train, station1, station2, verbose = False)
    time = get_passing_time_4blocks(blocks,bl_speed,data_path_check)
    if resolution == 1:
        time = round(time)
    return time

def minimal_stay(train,station,data,data_path_check,r=1):
    time_table = train_time_table(data,train)
    st_block = blocks_list_4station(data, train, station)
    id_station = get_indexes(time_table,st_block[0])[0][0]
    blocks_list = delta.iloc[id_station:id_station+2]["path"].tolist()
    block_speed_list = delta.iloc[id_station:id_station+2]["speed"].tolist()
    time = get_passing_time_4blocks(blocks_list,block_speed_list,data_path_check)
    if r==1:
        time = round(time)
    return time