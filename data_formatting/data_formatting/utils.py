import pandas as pd
import numpy as np
from collections import defaultdict
from .time_table_check import get_passing_time_4blocks, timetable_to_train_dict
from .time_table_check import train_important_stations
from .time_table_check import train_time_table


def getSizeOfNestedList(listOfElem):
    """
    Get number of elements in a nested list

    return total number of elements in list of lists
    """
    count = 0
    # Iterate over the list
    for elem in listOfElem:
        # Check if type of element is list
        if type(elem) == list:
            # Again call this function to get the size of this element
            count += getSizeOfNestedList(elem)
        else:
            count += 1
    return count

def reverse_dict_of_lists(d):
    reversed_dict = defaultdict(list)
    for key, values in d.items():
        for value in values:
            reversed_dict[value].append(key)
    return reversed_dict

def flatten(t):
    """ make a single list of lists of lists """
    return [item for sublist in t for item in sublist]


def common_elements(list1, list2):
    """ get common elements, order such as in list1 """
    return [element for element in list1 if element in list2]


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


# generate sublists in order
def sub_lists(l,no_single = False):
    lists = []
    for i in range(len(l) + 1):
        for j in range(i):
            subsl = l[j: i]
            if no_single == True:
                if len(subsl)<2:
                    continue
            lists.append(subsl)
    return lists

# check if sequential items from a short list (short) is in the bigger list (bigger)
def sublist(l1,l2):
    s1=" ".join(str(i) for i in l1)
    s2=" ".join(str(i) for i in l2)
    if s1 in s2:
        return True
    else:
        return False


def check_common_station(data, train1, train2):
    """ get common stations of two trains, does not check order """
    paths_dict = get_Paths(data)
    return list(set(paths_dict[train1]).intersection(paths_dict[train2]))

def get_trains_with_same_stations(data):
    return reverse_dict_of_lists(get_Paths(data))

def check_common_blocks_elements(data , train1, train2):
    """ get common blocks between trains, does not check order """
    return common_elements(list(train_time_table(data, train1)['path']),list(train_time_table(data, train2)['path']))

# check which important station the block belongs to
def get_block_station(block):
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    return [key for key, value in important_stations.items() if block in value][0]

def blocks_list_4station(data, train, station):
    sts = get_Paths(data)[train]

    if station not in sts:
        print('Warning: this train does not pass through this station!')
        return []
    station_blocks = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()][station]
    time_table_blocks = train_time_table(data, train)['path'].tolist()
    return common_elements(station_blocks,time_table_blocks)

# get common blocks between stations, in order of the time table
def get_blocks_b2win_station4train(data, train,station1,station2, verbose = True):
    sts = get_Paths(data)[train]
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    blocksb2win = []
    rev = False
    if station1 not in sts and station2 in sts:
        print('Warning: station {} not in the train set'.format(station1))
        return [],None
    if station2 not in sts and station1 in sts:
        print('Warning: station {} not in the train set'.format(station2))
        return [],None
    if station2 not in sts and station1 not in sts:
        print('Warning: station {} and {} not in the train set'.format(station1,station2))
        return [],None
    # assert station1 in sts, 'station {} not in the train set'.format(station1)
    # assert station2 in sts, 'station {} not in the train set'.format(station2)
    if sts.index(station1) > sts.index(station2):
        if verbose == True:
            print("Warning: stations out of order")
        rev = True
        return blocksb2win, rev
    else:
        blocks_list = train_time_table(data, train)['path'].tolist()
        i = 0
        block = blocks_list[i]
        while block not in important_stations[station1]:
            i+=1
            block = blocks_list[i]
        while block not in important_stations[station2] and i<len(blocks_list)-1:
            blocksb2win.append(block)
            i+=1
            block = blocks_list[i]
        if len(blocksb2win)>0:
            if blocksb2win[0] in important_stations[station1]:
                blocksb2win.pop(0)
            if len(blocksb2win) > 0 and blocksb2win[-1] in important_stations[station2]:
                blocksb2win.pop(-1)
        return blocksb2win,rev

def check_common_specific_elements_lists(list1,list2):
    common_elements = []
    i = 0
    short = []
    while i in range(len(list1)):
        if list1[i] in list2:
            short.append(list1[i])
            if sublist(short,list2) and i<len(list1)-1:
                i+=1
            else:
                common_elements.append(short)
                short = []
                i+=1
        else:
            i+=1
    return common_elements

def get_common_blocks_and_direction_b2win_trains(data,train1,train2,station1,station2,verbose = False):
    blocks_order = {}
    for train in [train1,train2]:
        blocks,rev = get_blocks_b2win_station4train(data,train,station1,station2,verbose)
        if rev:
            blocks,_ = get_blocks_b2win_station4train(data, train,station2,station1,verbose)
        blocks_order[train] = [blocks,rev]
    common_blocks = check_common_specific_elements_lists(blocks_order[train1][0],blocks_order[train2][0])
    if blocks_order[train1][1] == blocks_order[train2][1]:
        direction = 'same'
    else:
        direction = 'opposite'
    # return common_blocks,direction
    return flatten(common_blocks),direction

def common_path(data,train1,train2,station1,station2,verbose=False):
    common_path_list = []
    blocks1,_ = get_blocks_b2win_station4train(data,train1,station1,station2,verbose)
    blocks2,_ = get_blocks_b2win_station4train(data,train2,station1,station2,verbose)
    if blocks1 == blocks2:
        common_path_list = blocks1
    else:
        common_path_list = flatten(check_common_specific_elements_lists(blocks1,blocks2))
    return common_path_list



def is_train_passing_thru_station(data, train, station):
    stations = get_Paths(data)[train]
    return station in stations

# get subsequent station for a given train
def subsequent_station(data, train, station):

    sts = get_Paths(data)[train]
    if station not in sts:
        # print( "The train does not pass trought this station!")
        return None
    if sts.index(station)==len(sts)-1:
        # print('This is the last station')
        return None
    return sts[sts.index(station)+1]


def get_trains_at_station(data,only_departue = False):

    trains_infor = timetable_to_train_dict(data)
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]

    trains_from_station = {}
    for station in important_stations.keys():
        trains_from_station[station] = []
        for train in trains_infor.keys():
            if only_departue == False:
                if trains_infor[train][1]['path'].isin(important_stations[station]).any():
                    trains_from_station[station].append(train)
            else:
                if trains_infor[train][1]['path'].isin(important_stations[station]).any() and trains_infor[train][1]['path'].isin(important_stations[station]).tolist()[-1]!=True:
                    trains_from_station[station].append(train)
    return trains_from_station


def get_J(data):
    """  return a dictionary of trains """
    train_dict = timetable_to_train_dict(data)
    return list(train_dict.keys())

def get_all_important_station():
    """ read important stations from file """
    return list(np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()].keys())


def get_Paths(data):
    """ return a dictonary of important stations, keys are trains numbers """
    trains = get_J(data)
    paths_per_train = {}
    for train in trains:
        paths_per_train[train] = train_important_stations(data, train)
    return paths_per_train

def minimal_passing_time(train,station1,station2,data,data_path_check,resolution=1):
    assert train in get_J(data),"train does not exist"
    assert station1 and station2 in train_important_stations(data, train)
    blocks,_,bl_speed = get_blocks_b2win_station4train(data, train, station1, station2, verbose = False)
    time = get_passing_time_4blocks(blocks,bl_speed,data_path_check)
    if resolution == 1:
        time = round(time)
    return time

def minimal_stay(train,station,data,data_path_check,r=1):
    time_table = train_time_table(data,train)
    st_block = blocks_list_4station(data, train, station)
    time = 0
    add_to_prep = {f"{train}_{station}":0}
    prep_flag = False
    for i in range(len(st_block)):
        id_station = get_indexes(time_table,st_block[i])[0][0]
        blocks_list = time_table.iloc[id_station:id_station+2]["path"].tolist()
        block_speed_list = time_table.iloc[id_station:id_station+2]["speed"].tolist()
        t = get_passing_time_4blocks(blocks_list,block_speed_list,data_path_check)
        if len(st_block)>1:
            turn_around = time_table.iloc[id_station]["Turnaround_time_minutes"]
            if np.isnan(turn_around)==False:
                if i>1:
                    t+=float(turn_around)
                else:
                    add_to_prep[f"{train}_{station}"] +=turn_around
                    prep_flag = True
        time+=t 
    if r==1:
        time = round(time)
    if prep_flag:
        return time,add_to_prep,prep_flag
    return time

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


def get_passing_time_4blocks(blocks_list,block_speed_list,data_path_check):
    assert len(blocks_list) > 1, "only one block? can't continue"
    time = 0
    for i in range(len(blocks_list)-1):
        value1,value2 = blocks_list[i:i+2]
        v1_speed = block_speed_list[i]
        data_check = data_path_check.loc[data_path_check["previous_block"].isin([value1,value2]) & data_path_check["next_block"].isin([value1,value2])]
        assert data_check.empty == False, "this combination is not valid"
        block_dir = get_indexes(data_check,value1)[0][1]
        speed_path = get_path_type_colunm(v1_speed,block_dir)
        time += float(data_check.iloc[0][speed_path])
        print(time)
    return time


