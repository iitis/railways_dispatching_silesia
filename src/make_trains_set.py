from time_table_check import *
import pandas as pd
from utils import *


def dict_generate(data, j, j_prime, s, s_prime, init_josingle):
    path = get_blocks_b2win_station4train(data, j, s, s_prime, verbose = False)[0]
    path_j_prime = get_blocks_b2win_station4train(data, j_prime, s_prime, s, verbose = False)[0]
    if len(path) != 0 and path == list(reversed(path_j_prime)):

        if (s,s_prime) in init_josingle.keys():
            init_josingle[(s, s_prime)].append([j, j_prime])
        else:
            init_josingle[(s, s_prime)] = [[j, j_prime]]

    elif len(list(set(path).intersection(path_j_prime))) != 0:
        assert 'partial common path is not supported'


def station_and_train_detail(data, imp_stations):
    if imp_stations != None:
        imp_stations_list = imp_stations
    else:
        imp_stations_list = get_all_important_station()
    trains_at_stations = get_trains_depart_from_station(data)
    return imp_stations_list, trains_at_stations


def josingle(data, imp_stations = None):

    init_josingle = {}
    imp_stations_list, trains_at_stations = station_and_train_detail(data, imp_stations)

    for s in imp_stations_list:

        for j in trains_at_stations[s]:

            s_prime = subsequent_station(data, j, s)

            if s_prime in imp_stations_list:

                for j_prime in trains_at_stations[s]:

                    if j_prime != j and s == subsequent_station(data, j_prime, s_prime):

                        if (s_prime , s) not in init_josingle.keys():
                            dict_generate(data, j, j_prime, s, s_prime, init_josingle)

    return init_josingle


if __name__ == "__main__":

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    #imp_stations = ['KL', 'Mi', 'MJ', 'KO', 'CB']
    imp_stations = ['KL', 'Mi', 'MJ']

    print(josingle(data, imp_stations))
