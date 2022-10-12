import pandas as pd
import numpy as np
from data_formatting import block_indices_to_interprete_switches, z_in, z_out, get_Paths
from data_formatting import train_time_table, blocks_list_4station
from data_formatting import update_all_timetables
from data_formatting import timetable_to_train_dict

data = pd.read_csv("../data/trains_schedules.csv", sep = ";")
data_paths = pd.read_excel("../data/network_paths.ods", engine="odf")
important_stations = np.load('../data/important_stations.npz',allow_pickle=True)['arr_0'][()]

time_tables_dict = timetable_to_train_dict(data)
train_dict = update_all_timetables(time_tables_dict,data_paths,important_stations)

def test_sets_of_switches():
    
    paths = get_Paths(train_dict)

    #  KL --  MJ --- Mi   segment

    j = 44862
    s = 'MJ'
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_in(data_paths, j, s, paths, station_block, blocks_list) == {2}
    assert z_out(data_paths, j, s, paths, station_block, blocks_list) == {1}

    j = 44717
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_in(data_paths, j, s, paths, station_block, blocks_list) == {1}
    assert z_out(data_paths, j, s, paths,  station_block, blocks_list) == {2}

    j = 44862
    s = 'KL'
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_in(data_paths, j, s, paths, station_block, blocks_list) == {78, 79, 83, 84, 85, 55, 56}
    assert z_out(data_paths, j, s, paths, station_block, blocks_list) == {8, 15}

    # KZ - KO(STM) - KO case

    j = 26103
    s = 'KZ'
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_out(data_paths, j, s, paths, station_block, blocks_list) == {53, 47}

    s = 'KO(STM)'
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_in(data_paths, j, s, paths, station_block, blocks_list) == {18, 5}
    assert z_out(data_paths, j, s, paths, station_block, blocks_list) == {55, 54, 39}

    s = 'KO'
    station_block = {j: blocks_list_4station(train_dict[j][1], s,important_stations)}
    blocks_list = {j: train_time_table(train_dict,j)['path'].tolist()}
    assert z_in(data_paths, j, s, paths, station_block, blocks_list) == {55, 54, 39}
