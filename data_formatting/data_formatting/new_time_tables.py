import numpy as np
import pandas as pd

from .utils import get_indexes, get_block_station

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
    return list(map(lambda x: single_passing_time(x,data_paths),blocks_info)).append(np.nan) #last station NaN

# def add_passing_time_time_table(timetable,data_paths):
#     timetable["passing_time"] = passing_times_4blocks(timetable,data_paths)

# def add_important_stations_time_table(timetable,important_stations):
#     timetable["important_station"] = list(map(lambda x: get_block_station(x,important_stations),timetable["paths"].tolist()))

def update_all_timetables(time_tables_dict,data_paths,important_stations,save = False):
    for key in time_tables_dict.keys():
        time_tables_dict[key][1]["passing_time"] = passing_times_4blocks(time_tables_dict[key][1],data_paths)
        time_tables_dict[key][1]["important_station"] = list(map(lambda x: get_block_station(x,important_stations),time_tables_dict[key][1]["path"].tolist()))
    if save = True:
        with open('update_tables.pkl', 'wb') as f:
            pickle.dump(time_tables_dict, f)
    return time_tables_dict

# class Block:
#     def __init__(self, name, speed, arr=None, derp=None, approx_enter=None, label=None, shuting=None, turnaround_time_minutes=0):
#         self.name = name
#         self.speed = speed
#         self.arr = arr
#         self.derp = derp
#         self.approx_enter = approx_enter
#         self.label = label
#         self.shuting = shuting
#         self.turnaround_time_minutes = turnaround_time_minutes

# class TimeTableBlocks:
#     def __init__(self):
#         self.time_table_blocks = []
    
#     def __getitem__(self,name):
#         return next((block for block in self.time_table_blocks if block.name == name), None)
    
#     def get_previous(self,block):
#         return None

#     def get_next(self,block):
#         return None

#     def passing_time(self,block): #TODO: it depends on next block.
#         return None

# class TimeTable:
#     def __init__(self, train, blocks, info):
#         """Constructor  for the TimeTable class

#         :param train: Train id
#         :type train: int
#         :param blocks: train blocks
#         :type end: list
#         :param info: Extra info of the time_table
#         :type weight: list
#         """
#         self.train = train
#         self.blocks = blocks
#         self.info = info

#     def __repr__(self):
#         """Used for printing

#         :return: String representation of the object
#         :rtype: string
#         """
#         return f"TimeTable for train no: {self.train} \n"


# class TimeTableCollector:
#     def __init__(self):
#         """Constructor for the TimeTableCollector class"""

#         self.time_tables = {}

#     def new_timetable(self, train, blocks, info)-> TimeTable:
#         """Creates a new time_table

#         :param start: Start time
#         :type start: int
#         :param end: End time
#         :type end: int
#         :param weight: Weight of the time_table
#         :type weight: float
#         :param track: track information for music files
#         :type track: int
#         :return: Created time_table
#         :rtype: TimeTable
#         """
#         time_table = TimeTable(train, blocks, info)
#         self += time_table
#         return time_table

#     def __add__(self, time_table: TimeTable) -> "TimeTableCollector":
#         """Adds a time_table to the time_table list of the TimeTableCollector

#         :param time_table: TimeTable to add
#         :type time_table: TimeTable
#         :return: TimeTableCollector object
#         :rtype: TimeTableCollector
#         """
#         if self[time_table.train] == None:
#             self.time_tables[time_table.train]=time_table
#         else:
#             print(f"TimeTable for train {time_table.train} already exists")
#         return self

#     def __getitem__(self, train) -> TimeTable:
#         """Returns the time_table with the given train, None if it is not found

#         :param id: train number of the time_table
#         :type id: int
#         :return: time_table with the given train number
#         :rtype:TimeTable
#         """
#         return next(self.time_tables[train], None)

#     def __repr__(self):
#         """Used for printing

#         :return: String representation of the object
#         :rtype: string
#         """
#         return self.time_tables.__repr__()
