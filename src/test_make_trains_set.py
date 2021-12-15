from utils import *

train1,train2 = 94611, 14006
station1,station2 = 'KO', 'KL'
data = pd.read_csv("../data/train_schedule.csv", sep = ";")

#print('"J":',get_J(data),'\n')
#print('"Paths":',get_Paths(data))
print('Common station for trains {} and {}:'.format(train1,train2),check_common_station(train1,train2,data))
print('Jround',get_jround(data))
print('block between stations {} and {} for train {}'.format(station1,station2,train1), get_blocks_b2win_station4train(train1,station1,station2))
# the last is not yet working
print('common blocks between stations {} and {} for train {} and train {}'.format(station1,station2,train1,train2), get_common_blocks_and_direction_b2win_trains(train1,train2,station1,station2))
