import pandas as pd
import numpy as np
from collections import defaultdict
from .time_table_check import timetable_to_train_dict
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
        return blocksb2win, reversed
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

def get_common_blocks_and_direction_b2win_trains(data,train1,train2,station1,station2,verbose = False):
    blocks_order = {}
    for train in [train1,train2]:
        blocks,rev = get_blocks_b2win_station4train(data,train,station1,station2,verbose)
        if rev:
            blocks,_ = get_blocks_b2win_station4train(data, train,station2,station1,verbose)
        blocks_order[train] = [blocks,rev]
    blocks_2check = blocks_order[train1][0]
    common_blocks = []
    i = 0
    short = []
    while i in range(len(blocks_2check)):
        if blocks_2check[i] in blocks_order[train2][0]:
            short.append(blocks_2check[i])
            if sublist(short,blocks_order[train2][0]) and i<len(blocks_2check)-1:
                i+=1
            else:
                common_blocks.append(short)
                short = []
                i+=1
        else:
            i+=1
    if blocks_order[train1][1] == blocks_order[train2][1]:
        direction = 'same'
    else:
        direction = 'opposite'
    # return common_blocks,direction
    return flatten(common_blocks),direction

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



# def get_trains_depart_from_station(data):
#
#     trains_infor = timetable_to_train_dict(data)
#     important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
#
#     trains_from_station = {}
#     for station in important_stations.keys():
#         trains_from_station[station] = []
#         for train in trains_infor.keys():
#             if trains_infor[train][1]['path'].isin(important_stations[station]).any() and trains_infor[train][1]['path'].isin(important_stations[station]).tolist()[-1]!=True:
#                 trains_from_station[station].append(train)
#     return trains_from_station

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
