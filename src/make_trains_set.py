from time_table_check import *
import re

data = pd.read_csv("../data/train_schedule.csv", sep = ";")

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
def check_sequential_elements(short,bigger):
    if re.search("".join(short),"".join(short)):
        return True
    else:
        return False

# return a dictionary of trains
def get_J(data):
    train_dict = timetable_to_train_dict(data)
    return list(train_dict.keys())

# return a dictonary of important stations
def get_Paths(data):
    trains = get_J(data)
    paths_per_train = {}
    for train in trains:
        paths_per_train[train] = check_important_stations(train)
    return paths_per_train

# get common station betwenn two trains, does not check order
def check_common_station(train1,train2):
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
def get_block_b2win_station4train(train,station1,station2):
    station1 = '"'+station1
    if station2 != '"KO", "ST-M"':
        station2 = '"'+station2
    blocks_list = train_time_table(train)['path']
    i = 0
    block = blocks_list[i]
    blocksb2win = []
    while block[0:len(station1)] != station1:
        i+=1
        block = blocks_list[i]
    while block[0:len(station2)] != station2:
        i+=1
        block = blocks_list[i]
        blocksb2win.append(block)
    blocksb2win.pop(0)
    blocksb2win.pop(-1)
    return blocksb2win

# get subsequent station for a given train
def subsequent_station(train,station):
    sts = get_Paths(data)[train]
    assert station in sts, "The train does not pass trought this station!"
    return sts[sts.index(station)+1]

# check shared stations between trains, does not check order
def get_trains_with_same_stations(data):
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    jdict = {}
    for station in list(important_stations.keys()):
        nextstation_dict = {}
        trains = []
        for train, path in list(path_dict.items()):
            if station in path and path.index(station)!=len(path)-1:
                trains += [train]
                nextstation_dict[path[path.index(station)+1]] =[trains]
        jdict[station] = nextstation_dict
    return jdict

# get list of train with pairs containing a train number and train number+9
def get_trains_pair9(data):
    trains = get_J(data)
    pair_lists = []
    for train in trains:
        if train*10+9 in trains:
            pair_lists+=[[train,train*10+9]]
    return pair_lists

def get_jround():
    important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    pair_lists = get_trains_pair9(data)
    print(pair_lists)
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
# train_sets = {
#
# }
