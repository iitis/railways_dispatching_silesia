from tkinter.tix import Tree
from utils import *
from make_trains_set import *

train1 = 44717
train2 =  44862
station1 = "Mi"
station2 =  "MJ"
imp_stations = ["MJ"]
data = pd.read_csv("../data/train_schedule.csv", sep = ";")
data_switch = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

print('"J":',get_J(data),'\n')
print('"Paths":',get_Paths(data))
print(f'\nCommon station for trains {train1} and {train2}:', check_common_station(data, train1,train2))
print('\nJround', get_jround(data))
print(f'\nblock between stations {station1} and {station2} for train {train1}', get_blocks_b2win_station4train(data, train1, station1, station2))
# the last is not yet working (now working)
print(f'\ncommon blocks between stations {station1} and {station2} for train {train1} and train {train2}', get_common_blocks_and_direction_b2win_trains(data,train1, train2,station1,station2))
print(f'\ntrains departuring from station {station1}', get_trains_at_station(data, True)[station1])
print(f'\nbetween stations {imp_stations} the following trains shares a single track while going in opposite direction as follows:')

imp_stations_s = ["KL", "MJ", "Mi"]
print(josingle(data, imp_stations_s))
print()
print(f'\n the list of trains that occupy particular station block is given below:')
print(jtrack(data))
print()
print(f'\nfor important station {imp_stations} the jswitches are:')
switch = jswitch(data, data_switch, imp_stations)
print(switch)
