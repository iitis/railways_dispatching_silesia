from utils import *
import sys
import random

data = pd.read_csv("../data/train_schedule.csv", sep = ";")
train_dict = timetable_to_train_dict(data)
trains_list = list(train_dict.keys())

if len(sys.argv) < 2:
    print("The available trains are:", *trains_list)
    exit(0)

train = int(sys.argv[1])

if train in trains_list:
    print('The train number is', train,'\n')
else:
    # train = random.choice(trains_list)
    print('\nThis train is not listed.\n')
    print('The available trains are:', *trains_list)
    exit()

schemes,station_ind = get_schmes(train,return_index = True)
arr_dep_vals = get_arr_dep_vals(train)
cumulative_time = 0
for i in range(len(schemes)):
    print('Checking time for path {} to {}'.format(train_time_table(train)['path'][schemes[i][0]],train_time_table(train)['path'][schemes[i][-1]+1]))
    station_time = 'N/A'
    arr_dep_time = 'N/A'
    check_start = 0
    total_time,times = check_path_time(train,schemes[i])
    if len(list(set(schemes[i]).intersection(station_ind))) !=0:
        station_time = times[0][-1]
        value = list((set(schemes[i]).intersection(station_ind)))[0]
        arr_dep_time = get_arrdep(train).loc[value].dropna().tolist()
        check_start=+1
        if pd.isnull(get_arrdep(train).loc[value]['Approx_enter'])== False:
            print('Approximate enter',get_arrdep(train).loc[value]['Approx_enter'])
        else:
            print('Arrival and departure times:',arr_dep_time)

    blocks_time = sum([times[n][-1] for n in range(check_start,len(times))])
    cumulative_time+=total_time

    print('Station stay time:{},'.format(station_time),'blocks passing time: {}'.format(np.round(blocks_time,1)),"Total time is:",np.round(total_time,1),'cumulative time is:',np.round(cumulative_time,1),'\n')
    # print('For each block {}'.format(times),'\n')
if len(arr_dep_vals) - len(schemes) == 1:
    print('The last station {}: {}'.format(train_time_table(train)['path'][schemes[-1][-1]],arr_dep_vals[-1]))

total_time_path,_ = check_path_time(train,scheme=range(schemes[0][0],schemes[-1][-1]+1),show_warning = False)
print("The total time for whole path is {}".format(np.round(total_time_path,1)))
print("The important stations are:",check_important_stations(train))
    # for train in list(train_dict.keys()):
    #     total_time,times = check_path_time(train)
    #     print("Total time is:",total_time)
    #     print("For each path",times)
