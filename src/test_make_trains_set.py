from make_trains_set import *

train1,train2 = 94766,26103
print('"J":',get_J(data),'\n')
print('"Paths":',get_Paths(data))
print('Common station for trains {} and {}:'.format(train1,train2),check_common_station(train1,train2))
print('Jround',get_jround())
