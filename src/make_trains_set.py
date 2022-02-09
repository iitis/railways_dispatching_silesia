from pytest import skip
from time_table_check import *
import pandas as pd
from utils import *
from test_jswitch import *


def josingle_dict_generate(data, j, j_prime, s, s_prime, init_josingle):
    path = get_blocks_b2win_station4train(data, j, s, s_prime, verbose = False)[0]
    path_j_prime = get_blocks_b2win_station4train(data, j_prime, s_prime, s, verbose = False)[0]
    if len(path) != 0 and path == list(reversed(path_j_prime)):

        if (s,s_prime) in init_josingle.keys():
            init_josingle[(s, s_prime)].append([j, j_prime])
        else:
            init_josingle[(s, s_prime)] = [[j, j_prime]]

    elif len(list(set(path).intersection(path_j_prime))) != 0:
        assert 'partial common path is not supported'

def jtrack_dict_generation(Jtrack_dict):
    Jtrack_mod = {}
    for key in Jtrack_dict.keys():
        Jtrack_mod[key] = []
        for el in Jtrack_dict[key]:
            if len(el) != 0:
                Jtrack_mod[key].append(el)

    return Jtrack_mod


def important_trains_and_stations(data, imp_stations, only_departue):
    if imp_stations != None:
        imp_stations_list = imp_stations
    else:
        imp_stations_list = get_all_important_station()
    trains_at_stations = get_trains_at_station(data, only_departue)
    return imp_stations_list, trains_at_stations



def exclusion_list_jtrack():
    station_exclusion_list = ['KO(KS)', 'KO(IC)']
    block_exclusion_list = [['"KO", "ST-M", 1114, "(N/A)"'], ['"KO", "ST-M", 1113, "(N/A)"'], ['"KO", "ST-M", 1118, "(N/A)"']]
    return station_exclusion_list, block_exclusion_list

def non_repeating_pair_for_jswitch():
    non_repeating_pair = [ ['KO', 'KO(STM)'] , ['KO(IC)', 'KO(STM)'] , ['KO', 'KO(KS)'] ]
    return non_repeating_pair

def josingle(data, imp_stations = None):

    init_josingle = {}
    imp_stations_list, trains_at_stations = important_trains_and_stations(data, imp_stations, True)

    for s in imp_stations_list:
        for j in trains_at_stations[s]:

            s_prime = subsequent_station(data, j, s)
            if s_prime in imp_stations_list:
                for j_prime in trains_at_stations[s]:
                    if j_prime != j and s == subsequent_station(data, j_prime, s_prime):
                        if (s_prime , s) not in init_josingle.keys():
                            josingle_dict_generate(data, j, j_prime, s, s_prime, init_josingle)

    return init_josingle



def jtrack(data, imp_stations = None):

    init_jtrack = {}
    imp_stations_list, trains_at_stations = important_trains_and_stations(data, imp_stations, False)
    station_exclusion_list, block_exclusion_list = exclusion_list_jtrack()

    for s in imp_stations_list:

        if s not in station_exclusion_list:
            vs = [[]]
            current_blocks = []

            for j in trains_at_stations[s]:

                b = blocks_list_4station(data, j, s)

                if b not in block_exclusion_list:

                    if b in current_blocks:

                        i = current_blocks.index(b)+1
                        vs[i].append(j)
                    else:
                        vs.append([j])
                        current_blocks.append(b)

            if len(vs) != 0:
                init_jtrack[s] = vs

    return jtrack_dict_generation(init_jtrack)



def jswitch(data, data_switch, imp_stations = None):

    jswitch = {}

    imp_stations_list, trains_at_stations = important_trains_and_stations(data, imp_stations, True)
    non_repeat_pair = non_repeating_pair_for_jswitch()

    for s in imp_stations_list:

        vec_of_pairs = []

        for j in trains_at_stations[s]:

            for jprime in trains_at_stations[s]:

                if jprime != j:

                    in_switch_sequence_j = z_in(data, data_switch, j, s)
                    out_switch_sequence_j = z_out(data, data_switch, j, s)
                    in_switch_sequence_jprime = z_in(data, data_switch, jprime, s)
                    out_switch_sequence_jprime = z_out(data, data_switch, jprime, s)


                    if ( len(in_switch_sequence_j) != 0 and len(in_switch_sequence_jprime) != 0 and

                        len( list( set(in_switch_sequence_j) & set(in_switch_sequence_jprime) ) ) != 0 ):

                        print(len(in_switch_sequence_j), len(in_switch_sequence_jprime))

                        vec_of_pairs.append( { j : "in" , jprime : "in" } )


                    elif ( len(in_switch_sequence_j) != 0 and len(out_switch_sequence_jprime) != 0 and

                        len( list( set(in_switch_sequence_j) & set(out_switch_sequence_jprime) ) ) != 0 ):

                        vec_of_pairs.append( { j : "in" , jprime : "out" } )

                        print(len(in_switch_sequence_j), len(out_switch_sequence_jprime))


                    elif  ( len(out_switch_sequence_j) != 0 and len(in_switch_sequence_jprime) != 0 and

                        len( list( set(out_switch_sequence_j) & set(in_switch_sequence_jprime) ) ) != 0 ):

                        vec_of_pairs.append( { j : "out" , jprime : "in" } )
                        print(len(out_switch_sequence_j), len(in_switch_sequence_jprime))


                    elif ( len(out_switch_sequence_j) != 0 and len(out_switch_sequence_jprime) != 0  and

                        len( list( set(out_switch_sequence_j) & set(out_switch_sequence_jprime) ) ) != 0 ):

                        vec_of_pairs.append( { j : "out" , jprime : "out" } )
                        print(len(out_switch_sequence_j), len(out_switch_sequence_jprime))

                    print(vec_of_pairs)


        jswitch[s] = vec_of_pairs

    return jswitch




if __name__ == "__main__":

    # exit()

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    data_switch = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
    #imp_stations = ['KL', 'Mi', 'MJ', 'KO', 'CB']
    imp_stations = ['KO(STM)']

    # print(josingle(data, imp_stations))
    # print(jtrack(data, imp_stations))


    switch = jswitch(data, data_switch, imp_stations = ['KZ'])

    print(switch)
