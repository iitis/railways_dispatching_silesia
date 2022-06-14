import pandas as pd
import sys
import random

from data_formatting import timetable_to_train_dict

### prints the timetable of the train ###

data = pd.read_csv("../data/train_schedule.csv", sep = ";")
data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

train_dict = timetable_to_train_dict(data)
trains_list = list(train_dict.keys())

# some indexing
def get_schmes(data, train, return_index = False):
    arrdep = get_arrdep(data, train)
    indexs = list(arrdep.dropna(how='all').index)
    a = indexs.copy()
    b_list = []
    for i in range(len(a)-1):
        b_list+= [list(range(a[i],a[i+1]))]
    if return_index == True:
        return b_list, indexs
    return b_list

# check path directions and type: A to B or B to A, regional or intercity
def get_path_type_colunm(path_type,block_dir):
    if path_type in ['R']:
        if block_dir == 'previous_block':
            path_column  = 'time_regional_train_A-B'
        else:
            path_column  = 'time_regional_train_B-A'
    elif path_type in ['IC']:
        if block_dir == 'previous_block':
            path_column = 'time_inter_city_A-B'
        else:
            path_column = 'time_inter_city_B-A'
    else:
        print('Path type not found!')
        exit(1)
    return path_column

# check path default
def get_default_dir(path_column):
    if path_column in ['time_regional_train_A-B','time_inter_city_A-B']:
        default_dir = 'default_A-B'
    else:
        default_dir = 'default_B-A'
    return default_dir



# check paths time
def check_path_time(train, data, data_path_check, scheme = 'complete', show_warning = True):
    """  compute passing time from the given tiletable """
    train_dict = timetable_to_train_dict(data)
    time_table = train_dict[train][1]

    print('This line belongs to', train_dict[train][0][0])
    if scheme == 'complete':
        scheme = list(range(len(time_table)-1))
    times = []
    total_time = 0
    for i in scheme:
        path_type = time_table.iloc[i]['speed']
        positions_in_table_check = get_indexes(data_path_check,time_table['path'][i])
        assert len(positions_in_table_check) > 0 ,"{} not found".format(time_table['path'][i])
        for x in positions_in_table_check:
            if x[0] in [y[0] for y in get_indexes(data_path_check,time_table['path'][i+1])]:
                position,block_dir = x
                # print("The position is", position)
                # print("The block direction is", block_dir)
            # else:
            #     print('the entry does not exist!')
            #     exit()
        path_column  = get_path_type_colunm(path_type,block_dir)
        # print(path_column)
        # print(get_default_dir(path_column))
        # print(data_path_check.iloc[position][get_default_dir(path_column)])
        default_dir = get_default_dir(path_column)
        if show_warning == True:
            if data_path_check.iloc[position][default_dir] == 'N' and time_table['Shunting'][i+1] == 'N':
                print('Warning: {} {} is not default'.format(data_path_check.iloc[position][0:2].tolist(),default_dir))
            if  time_table['Shunting'][i] == 'Y' and data_path_check.iloc[position][default_dir] == 'N':
                    print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
                # elif time_table['Shunting'][i] == 'Y':
            elif time_table['Shunting'][i+1] == 'Y' and data_path_check.iloc[position][default_dir] == 'N':
                print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
                # else:
                #     print("Warning: the route",time_table['path'][i],"to",time_table['path'][i+1],"is not default!", "for train No.", train, "name",  train_dict[train][0][1])
        time_passed = float(data_path_check.iloc[position][path_column])
        if np.isnan(time_table.iloc[i]['Turnaround_time_minutes']) == False:
            time_passed+= time_table.iloc[i]['Turnaround_time_minutes']
        total_time += time_passed
        times += [[time_table['path'][i], time_table['path'][i+1],time_passed]]
    return total_time,times






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

schemes,station_ind = get_schmes(data,train,return_index = True)
arr_dep_vals = get_arr_dep_vals(data,train)
cumulative_time = 0
for i in range(len(schemes)):
    print('Checking time for path {} to {}'.format(train_time_table(data,train)['path'][schemes[i][0]],train_time_table(data,train)['path'][schemes[i][-1]+1]))
    station_time = 'N/A'
    arr_dep_time = 'N/A'
    check_start = 0
    total_time,times = check_path_time(train,data,data_path_check,schemes[i])
    if len(list(set(schemes[i]).intersection(station_ind))) !=0:
        station_time = times[0][-1]
        value = list((set(schemes[i]).intersection(station_ind)))[0]
        arr_dep_time = get_arrdep(data,train).loc[value].dropna().tolist()
        check_start=+1
        if pd.isnull(get_arrdep(data,train).loc[value]['Approx_enter'])== False:
            print('Approximate enter',get_arrdep(data,train).loc[value]['Approx_enter'])
        else:
            print('Arrival and departure times:',arr_dep_time)

    blocks_time = sum([times[n][-1] for n in range(check_start,len(times))])
    cumulative_time+=total_time

    print('Station stay time:{},'.format(station_time),'blocks passing time: {}'.format(np.round(blocks_time,1)),"Total time is:",np.round(total_time,1),'cumulative time is:',np.round(cumulative_time,1),'\n')
    # print('For each block {}'.format(times),'\n')
if len(arr_dep_vals) - len(schemes) == 1:
    print('The last station {}: {}'.format(train_time_table(data,train)['path'][schemes[-1][-1]],arr_dep_vals[-1]))

total_time_path,_ = check_path_time(train,data,data_path_check,scheme=range(schemes[0][0],schemes[-1][-1]+1),show_warning = False)
print("The total time for whole path is {}".format(np.round(total_time_path,1)))
print("The important stations are:",check_important_stations(data,train))
    # for train in list(train_dict.keys()):
    #     total_time,times = check_path_time(train)
    #     print("Total time is:",total_time)
    #     print("For each path",times)
