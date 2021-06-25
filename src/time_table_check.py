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
    if path_type in ['KS - Os','KS - OsP','PR - R']:
        if block_dir == 'previous_block':
            path_column  = 'time_regional_train_A-B'
        else:
            path_column  = 'time_regional_train_B-A'
    elif path_type in ['IC - IC','IC - TLK','IC - EIP']:
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

# check paths time
def check_path_time(train, scheme = 'complete'):
    train_dict = timetable_to_train_dict(data)
    data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
    path_type,time_table = train_dict[train][0][0], train_dict[train][1]
    print(path_type)
    if scheme == 'complete':
        scheme = list(range(len(time_table)-1))
    times = []
    total_time = 0
    for i in scheme:
        for x in get_indexes(data_path_check,time_table['path'][i]):
            if x[0] in [y[0] for y in get_indexes(data_path_check,time_table['path'][i+1])]:
                position,block_dir = x
                # print("The position is", position)
                # print("The block direction is", block_dir)
        path_column  = get_path_type_colunm(path_type,block_dir)
        if data_path_check.iloc[position][get_default_dir(path_column)] == 'N':
            if  train_dict[train][1]['Shunting'][i+1] == 'Y':
                print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
            elif train_dict[train][1]['Shunting'][i] == 'Y':
                    print("Non default shunting ",time_table['path'][i],"to",time_table['path'][i+1], "for train No.", train, "name",  train_dict[train][0][1])
            else:
                print("Warning: the route",time_table['path'][i],"to",time_table['path'][i+1],"is not default!", "for train No.", train, "name",  train_dict[train][0][1])
        time_passed = float(data_path_check.iloc[position][path_column])
        total_time += time_passed
        times += [[time_table['path'][i]+' to '+ time_table['path'][i+1],time_passed]]
    return total_time,times

if __name__ == "__main__":

    train = 94766

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    train_dict = timetable_to_train_dict(data)

    print("The trains are:", *list(train_dict.keys()))
    print()
    for train in list(train_dict.keys()):
        total_time,times = check_path_time(train)
        print("Total time is:",total_time)
    #print("For each path",times)
