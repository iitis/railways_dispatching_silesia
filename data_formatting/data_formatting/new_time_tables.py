import numpy as np
import pandas as pd
import pickle
from .utils import get_indexes, get_block_station, get_path_type_colunm

data = pd.read_csv("../data/train_schedule.csv", sep = ";")
data_paths = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]


def single_passing_time(block_info,data_paths):
    value1,value2,v1_speed = block_info
    data_check = data_paths.loc[data_paths["previous_block"].isin([value1,value2]) & data_paths["next_block"].isin([value1,value2])]
    assert data_check.empty == False, f"this combination: {value1} and {value2} is not valid"
    block_dir = get_indexes(data_check,value1)[0][1]
    speed_path = get_path_type_colunm(v1_speed,block_dir)
    return float(data_check.iloc[0][speed_path])

def passing_times_4blocks(timetable,data_paths):
    blocks = timetable["path"].tolist()
    speed  = timetable["speed"].to_list()
    blocks_info = list(zip(blocks[:],blocks[1:],speed))
    passing_time = list(map(lambda x: single_passing_time(x,data_paths),blocks_info))
    passing_time.append(np.nan) #last station NaN. It does not have passing time
    return  passing_time 

def update_all_timetables(time_tables_dict,data_paths,important_stations,save = False):
    for key in time_tables_dict.keys():
        time_tables_dict[key][1]["passing_time"] = passing_times_4blocks(time_tables_dict[key][1],data_paths)
        time_tables_dict[key][1]["important_station"] = list(map(lambda x: get_block_station(x,important_stations),time_tables_dict[key][1]["path"].tolist()))
    if save == True:
        with open('update_tables.pkl', 'wb') as f:
            pickle.dump(time_tables_dict, f)
    return time_tables_dict
