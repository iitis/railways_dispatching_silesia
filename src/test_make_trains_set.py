from make_trains_set import *

train1,train2 = 44862,44717
station1,station2 = 'Mi','MJ'
data = pd.read_csv("../data/train_schedule.csv", sep = ";")

#print('"J":',get_J(data),'\n')
#print('"Paths":',get_Paths(data))
print('Common station for trains {} and {}:'.format(train1,train2),check_common_station(train1,train2,data))
print('Jround',get_jround(data))
print('block between stations {} and {} for train {}'.format(station1,station2,train1), get_block_b2win_station4train(train1,station1,station2))
