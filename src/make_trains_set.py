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

# train_sets = {
#
# }
if __name__ == "__main__":
    print('"J":',get_J(data),'\n')
    print('"Paths":',get_Paths(data))
