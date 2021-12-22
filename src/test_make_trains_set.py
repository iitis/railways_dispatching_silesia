from utils import *

train1,train2 =  44717, 44862
station1,station2 = "Mi", "KL"
data = pd.read_csv("../data/train_schedule.csv", sep = ";")

#print('"J":',get_J(data),'\n')
#print('"Paths":',get_Paths(data))
print('\nCommon station for trains {} and {}:'.format(train1,train2),check_common_station(train1,train2,data))
print('\nJround',get_jround(data))
print('\nblock between stations {} and {} for train {}'.format(station1,station2,train1), get_blocks_b2win_station4train(train1,station1,station2))
# the last is not yet working
print('\ncommon blocks between stations {} and {} for train {} and train {}'.format(station1,station2,train1,train2), get_common_blocks_and_direction_b2win_trains(train1,train2,station1,station2))
print(f'\ntrains departuring from station {station1}',get_trains_depart_from_station()[station1])
