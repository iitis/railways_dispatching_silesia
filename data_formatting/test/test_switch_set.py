import pandas as pd
from data_formatting import block_indices_to_interprete_switches, z_in, z_out, get_Paths
from data_formatting import train_time_table, blocks_list_4station


def test_sets_of_switches():

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    paths = get_Paths(data)

    #  KL --  MJ --- Mi   segment

    j = 44862
    s = 'MJ'
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_in(data_path_check, j, s, paths, station_block, blocks_list) == {2}
    assert z_out(data_path_check, j, s, paths, station_block, blocks_list) == {1}

    j = 44717
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_in(data_path_check, j, s, paths, station_block, blocks_list) == {1}
    assert z_out(data_path_check, j, s, paths,  station_block, blocks_list) == {2}

    j = 44862
    s = 'KL'
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_in(data_path_check, j, s, paths, station_block, blocks_list) == {78, 79, 83, 84, 85, 55, 56}
    assert z_out(data_path_check, j, s, paths, station_block, blocks_list) == {8, 15}

    # KZ - KO(STM) - KO case

    j = 26103
    s = 'KZ'
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_out(data_path_check, j, s, paths, station_block, blocks_list) == {53, 47}

    s = 'KO(STM)'
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_in(data_path_check, j, s, paths, station_block, blocks_list) == {18, 5}
    assert z_out(data_path_check, j, s, paths, station_block, blocks_list) == {55, 54, 39}

    s = 'KO'
    station_block = {j: blocks_list_4station(data, j, s)}
    blocks_list = {j: train_time_table(data, j)['path'].tolist()}
    assert z_in(data_path_check, j, s, paths, station_block, blocks_list) == {55, 54, 39}
