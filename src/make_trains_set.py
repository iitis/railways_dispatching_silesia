from time_table_check import *

data = pd.read_csv("../data/train_schedule.csv", sep = ";")

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

def flatten(t):
    return [item for sublist in t for item in sublist]

def common_elements(list1, list2):
    return [element for element in list1 if element in list2]

def sublist(lst1, lst2):
    from collections import Counter
    c1 = Counter(lst1)
    c2 = Counter(lst2)
    for item, count in c1.items():
        if count > c2[item]:
            return False
    return True

def get_J(data):
    train_dict = timetable_to_train_dict(data)
    return list(train_dict.keys())

def get_Paths(data):
    trains = get_J(data)
    paths_per_train = {}
    for train in trains:
        paths_per_train[train] = check_important_stations(train)
    return paths_per_train

def check_common_station(train1,train2):
    paths_dict = get_Paths(data)
    return list(set(paths_dict[train1]).intersection(paths_dict[train2]))

def check_common_blocks_elements(train1,train2):
    return common_elements(list(train_time_table(train1)['path']),list(train_time_table(train2)['path']))

def sequential_elementsets_in_2lists(list1,list2):
    common_list_sets = []
    i = 0
    while i in range(len(list1)):
        if len(common_elements(list1[i:i+1], list2)) < 1:
            i+=1
        else:
            c=1
            blocks_seq = [list1[i]]
            while sublist(list1,list2) and i+c<len(list1):
                blocks_seq.append(list1[i+c])
                c+=1
            common_list_sets += [blocks_seq[0:-1]]
            i+=c
        return common_list_sets

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
