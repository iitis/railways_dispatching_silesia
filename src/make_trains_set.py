from time_table_check import *

data = pd.read_csv("../data/train_schedule.csv", sep = ";")

def get_J(data):
    train_dict = timetable_to_train_dict(data)
    return list(train_dict.keys())

def get_Paths(data):
    trains = get_J(data)
    paths_per_train = {}
    for train in trains:
        paths_per_train[train] = check_important_stations(train)
    return paths_per_train

def check_common_path(train1,train2):
    paths_dict = get_Paths(data)
    return list(set(paths_dict[train1]).intersection(paths_dict[train2]))

# train_sets = {
#
# }
if __name__ == "__main__":
    train1,train2 = 94766,26103
    print('"J":',get_J(data),'\n')
    print('"Paths":',get_Paths(data))
    print('Common path for trains {} and {}:'.format(train1,train2),check_common_path(train1,train2))
