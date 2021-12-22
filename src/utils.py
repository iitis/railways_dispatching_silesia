from time_table_check import *
import re
import pandas as pd

# return total number of elements in list of lists
def getSizeOfNestedList(listOfElem):
    ''' Get number of elements in a nested list'''
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

# make a single list of lists of lists
def flatten(t):
    return [item for sublist in t for item in sublist]

# get common elements, but without order
def common_elements(list1, list2):
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

# return a dictionary of trains
def get_J(data):
    train_dict = timetable_to_train_dict(data)
    return list(train_dict.keys())

def get_all_important_station():
    return list(np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()].keys())

# return a dictonary of important stations
def get_Paths(data):
    trains = get_J(data)
    paths_per_train = {}
    for train in trains:
        paths_per_train[train] = check_important_stations(train)
    return paths_per_train

# get common station betwenn two trains, does not check order
def check_common_station(train1,train2,data):
    paths_dict = get_Paths(data)
    return list(set(paths_dict[train1]).intersection(paths_dict[train2]))

# get common blocks between trains, does not check order
def check_common_blocks_elements(train1,train2):
    return common_elements(list(train_time_table(train1)['path']),list(train_time_table(train2)['path']))

# check which important station the block belongs to
def get_block_station(block):
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    return [key for key, value in important_stations.items() if block in value][0]

# get common blocks between stations, in order of the time table
def get_blocks_b2win_station4train(train,station1,station2, verbose = True):
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    sts = get_Paths(data)[train]
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    blocksb2win = []
    rev = False
    assert station1 in sts, 'station {} not in the train set'.format(station1)
    assert station2 in sts, 'station {} not in the train set'.format(station2)
    if sts.index(station1) > sts.index(station2):
        if verbose == True:
            print("Warning: stations out of order")
        rev = True
        return blocksb2win,reversed
    else:
        blocks_list = train_time_table(train)['path'].tolist()
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

def get_common_blocks_and_direction_b2win_trains(train1,train2,station1,station2,verbose = False):
    blocks_order = {}
    for train in [train1,train2]:
        blocks,rev = get_blocks_b2win_station4train(train,station1,station2,verbose)
        if rev:
            blocks,_ = get_blocks_b2win_station4train(train,station2,station1,verbose)
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

def is_train_passing_thru_station(train,station):
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    stations = get_Paths(data)[train]
    return station in stations

# get subsequent station for a given train
def subsequent_station(train, station):
    sts = get_Paths(data)[train]
    assert station in sts, "The train does not pass trought this station!"
    if sts.index(station)=len(sts)-1:
        print('This is the last station')
        return station
    return sts[sts.index(station)+1]

# get list of train with pairs containing a train number and train number+9
def get_trains_pair9(data):
    trains = get_J(data)
    pair_lists = []
    for train in trains:
        if train*10+9 in trains:
            pair_lists+=[[train,train*10+9]]
    return pair_lists
# return dict
def get_jround(data):
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    pair_lists = get_trains_pair9(data)
    jround = {}
    for pair in pair_lists:
        a = train_time_table(pair[0])['path'].tolist()[0] == train_time_table(pair[1])['path'].tolist()[-1]
        b = train_time_table(pair[1])['path'].tolist()[0] == train_time_table(pair[0])['path'].tolist()[-1]
        if a:
            block = (train_time_table(pair[0])['path'].tolist()[0])
            pair = list(reversed(pair))
        elif b:
            block = (train_time_table(pair[1])['path'].tolist()[0])
        else:
            print("Something is wrong")
            exit(1)
        station = [key for key, value in important_stations.items() if block in value][0]
        if station in jround.keys():
            jround[station].append(pair)
        else:
            jround[station]=[pair]
    return jround

def get_trains_depart_from_station():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    trains_infor = timetable_to_train_dict(data)
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]

    trains_from_station = {}
    for station in important_stations.keys():
        trains_from_station[station] = []
        for train in trains_infor.keys():
            if trains_infor[train][1]['path'].isin(important_stations[station]).any() and trains_infor[train][1]['path'].isin(important_stations[station]).tolist()[-1]!=True:
                trains_from_station[station].append(train)
    return trains_from_station
