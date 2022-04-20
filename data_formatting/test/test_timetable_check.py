from data_formatting import *

def test_timetables():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_path = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    t = get_arrdep(data, 42100) # should return arriving and dep times for blocks where they are given
    #print(t)

    timetable = timetable_to_train_dict(data)
    assert timetable[42100][0] == ['IC - IC', 'SZTYGAR', 'from Katowice', 'to Lublin Główny']

    print(timetable[42100][1]['path'][0])



def test_trains_paths():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_path = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")

    assert get_arr_dep_vals(data, 42100)[0][1] == '16:08'
    assert get_arr_dep_vals(data, 42100)[1][2] == '16:12'

    assert train_important_stations(data, 42100) == ['KO', 'KO(STM)', 'KZ']

    check_path_continuity(data, data_path.iloc[:,:2], 42100)
