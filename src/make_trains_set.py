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
# def train_blocks_b2win_stations(train,station1,station2):

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

def get_block_b2win_station4train(train,station1,station2):
    station1,station2 = '"'+station1,'"'+station2
    blocks_list = train_time_table(train1)['path'].tolist()
    i = 0
    block = blocks_list[i]
    blocksb2win = []
    while block[0:len(station1)] != station1:
        i+=1
        block = blocks_list[i]
    while block[0:len(station2)] != station2:
        block = blocks_list[i]
        i+=1
        blocksb2win.append(block)
    return blockb2win
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
# train_sets = {
#
# }
if __name__ == "__main__":
    train1,train2 = 94766,26103
    print('"J":',get_J(data),'\n')
    print('"Paths":',get_Paths(data))
    print('Common station for trains {} and {}:'.format(train1,train2),check_common_station(train1,train2))
