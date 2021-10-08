import pandas as pd
import numpy as np


# get indexes in dataframe
def get_indexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

# convert csv to dictionary
def timetable_to_train_dict(data):
    train_dict = {}
    for i in range(len(data['Unnamed: 0'])):
        if data['Unnamed: 0'][i].isnumeric():
            info = []
            train = int(data['Unnamed: 0'][i])
            info += [data['Unnamed: 0'][i-1]]
            info += [data['Unnamed: 0'][i+x] for x in range(1,3)]
        statment = data['Unnamed: 0'][i][0:4]
        if statment in ['from','depa']:
            tt_init = i+1
            tt_item = data['Unnamed: 0'][i+1]
            pa = 1
            while tt_item[0:2] not in ['to','te']:
                pa+=1
                tt_item = data['Unnamed: 0'][i+pa]
            train_data = data.iloc[tt_init:pa-1+tt_init].reset_index(drop=True).rename(columns={'Unnamed: 0': 'path'})
            info += [data['Unnamed: 0'][pa-1+tt_init]]
            train_dict[train] = [info,train_data]
    return train_dict

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
        error(1)
    return path_column

# check path default
def get_default_dir(path_column):
    if path_column in ['time_regional_train_A-B','time_inter_city_A-B']:
        default_dir = 'default_A-B'
    else:
        default_dir = 'default_B-A'
    return default_dir

def train_time_table(train):
    train_dict = timetable_to_train_dict(data)
    time_table = train_dict[train][1]
    return time_table

def get_arrdep(train):
    time_table = train_time_table(train)
    arrdep = time_table.loc[:,['Arr','Dep']]
    return arrdep

def get_schmes(train,return_index = False):
    arrdep = get_arrdep(train)
    indexs = list(arrdep.dropna(how='all').index)
    a = indexs.copy()
    if a[0] != 0:
        a.insert(0,0)
    if a[-1] != len(arrdep)-1:
        a.append(len(arrdep)-1)
    b_list = []
    for i in range(len(a)-1):
        b_list+= [list(range(a[i],a[i+1]))]
    if return_index == True:
        return b_list, indexs
    return b_list

def get_arr_dep_vals(train):
    arrdep = get_arrdep(train)
    short_list = arrdep.dropna(how='all')
    arr_dep_vals = []
    for i in range(len(short_list)):
        arr_dep_vals+=[short_list.iloc[i].tolist()]
    return arr_dep_vals

# check paths time
def check_path_time(train, scheme = 'complete', show_warning = True):
    train_dict = timetable_to_train_dict(data)
    data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
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
            if  time_table['Shunting'][i] == 'Y':
                    print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
                # elif time_table['Shunting'][i] == 'Y':
            elif time_table['Shunting'][i+1] == 'Y':
                print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
                # else:
                #     print("Warning: the route",time_table['path'][i],"to",time_table['path'][i+1],"is not default!", "for train No.", train, "name",  train_dict[train][0][1])
        time_passed = float(data_path_check.iloc[position][path_column])
        total_time += time_passed
        times += [[time_table['path'][i], time_table['path'][i+1],time_passed]]
    return total_time,times


if __name__ == "__main__":
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
            arr_dep_time = get_arrdep(train).loc[value].tolist()
            check_start=+1
        print('Arrival and departure times:',arr_dep_time)

        blocks_time = sum([times[n][-1] for n in range(check_start,len(times))])
        cumulative_time+=total_time

        print('Station stay time:{},'.format(station_time),'blocks passing time: {}'.format(np.round(blocks_time,1)),"Total time is:",np.round(total_time,1),'cumulative time is:',np.round(cumulative_time,1),'\n')
        # print('For each block {}'.format(times),'\n')
    if len(arr_dep_vals) - len(schemes) == 1:
        print('The last station {}: {}'.format(train_time_table(train)['path'][schemes[-1][-1]],arr_dep_vals[-1]))

    total_time_path,_ = check_path_time(train,show_warning = False)
    print("The total time for whole path is {}".format(np.round(total_time_path,1)))
        # for train in list(train_dict.keys()):
        #     total_time,times = check_path_time(train)
        #     print("Total time is:",total_time)
        #     print("For each path",times)
