from time_table_check import *

data = pd.read_csv("../data/train_schedule.csv", sep = ";")

def common_elements(list1, list2):
    return [element for element in list1 if element in list2]

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

def check_common_blocks(train1,train2):
    return common_elements(list(train_time_table(train1)['path']),list(train_time_table(train2)['path']))

def sequential_blocks_same_direction(train1,train2):
    blocks_list1, blocks_list2= list(time_table1['path']),list(time_table2['path'])
    common_path_list = []
    i = 0
    while i in range(len(blocks_list1)):
    if len(common_elements(blocks_list1[i:i+1], blocks_list2)) < 1:
        i+=1
    else:
        c=1
        blocks_seq = [blocks_list1[i]]
        while blocks_list1[i+c] in blocks_list2:
            blocks_seq.append(blocks_list1[i+c])
            c+=1
        common_path_list += [blocks_seq]
        i+=c
        print(i)

# def is_going2samedirection(train1,train2):
#     blocks_list1,blocks_list2 = list(train_time_table(train1)['path'],list(train_time_table(train2)['path']
#     for i in range(blocks_list1):
#
#     return

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
