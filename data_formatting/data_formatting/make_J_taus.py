from ast import Dict
from tabnanny import verbose
import pandas as pd
import numpy as np
import itertools
import pickle as pkl
from sympy import intersection
from .utils import common_path, flatten, get_J, get_passing_time_block, minimal_passing_time, minimal_stay, subsequent_block, turn_around_time
from .time_table_check import timetable_to_train_dict, train_time_table
from .utils import get_trains_at_station
from .utils import subsequent_station
from .utils import get_blocks_b2win_station4train
from .utils import get_all_important_station
from .utils import blocks_list_4station
from .utils import get_Paths
from .make_switch_set import z_in
from .make_switch_set import z_out
import itertools as it

# get list of train with pairs containing a train number and train number+9
def get_trains_pair9(train_dict):
    """
    Returns vector of pairs of train numbers such that the number of second
    is the number of first with 9 at the end.

    We expect such pairs to have the common rolling stock.

    The one with 9 at the end is shunting
    """
    trains = get_J(train_dict)
    pair_lists = []
    for train in trains:
        if train*10+9 in trains:
            pair_lists+=[[train,train*10+9]]
    return pair_lists

# return dict
def get_jround(train_dict,important_stations):
    """
    return dict with stations as keys, and a vector of pairs of trains
    with the same rolling stock. The change on the number occurs on the station
    that is the key.

    Order of trains in each pair is such as in real situation
    """
    # important_stations = np.load('./important_stations.npz',allow_pickle=True)['arr_0'][()]
    pair_lists = get_trains_pair9(train_dict)
    jround = {}
    for pair in pair_lists:
        a = train_time_table(train_dict, pair[0])['path'].tolist()[0] == train_time_table(train_dict, pair[1])['path'].tolist()[-1]
        b = train_time_table(train_dict, pair[1])['path'].tolist()[0] == train_time_table(train_dict, pair[0])['path'].tolist()[-1]
        if a:
            block = (train_time_table(train_dict, pair[0])['path'].tolist()[0])
            pair = list(reversed(pair))
        elif b:
            block = (train_time_table(train_dict, pair[1])['path'].tolist()[0])
        else:
            print("Something is wrong")
            exit(1)
        station = [key for key, value in important_stations.items() if block in value][0]
        if station in jround.keys():
            jround[station].append(pair)
        else:
            jround[station]=[pair]
    return jround



def josingle_dict_generate(train_dict, j, j_prime, s, s_prime, init_josingle):

    """
    Return:
    -------
    Josingle dictionary (finalized version)

    Inputs:
    -------
    --> data, j, j', s, s',
    --> init_josingle (the dictionary that initially considered)

    """
    # TODO: mark as deprecable, change notation
    time_table_j = train_dict[j][1]
    time_talbe_j_prime = train_dict[j_prime][1]
    path = get_blocks_b2win_station4train(time_table_j, s, s_prime, verbose = False)[0]
    path_j_prime = get_blocks_b2win_station4train(time_talbe_j_prime, s_prime, s, verbose = False)[0]
    if len(path) != 0 and path == list(reversed(path_j_prime)):

        if (s,s_prime) in init_josingle.keys():
            init_josingle[(s, s_prime)].append([j, j_prime])
        else:
            init_josingle[(s, s_prime)] = [[j, j_prime]]

    elif len(list(set(path).intersection(path_j_prime))) != 0:
        assert 'partial common path is not supported'

def jtrack_dict_generation(Jtrack_dict):

    """
    Return:
    -------
    Jtrack dictionary (finalized version)

    Inputs:
    -------
    ---> Jtrack_dict (the dictionary that initially considered)

    """

    Jtrack_mod = {}
    for key in Jtrack_dict.keys():
        Jtrack_mod[key] = []
        for el in Jtrack_dict[key]:
            if len(el) != 0:
                Jtrack_mod[key].append(el)

    return Jtrack_mod


def important_trains_and_stations(trains_dict, important_stations,imp_stations, only_departue):

    """
    Return:
    -------
    --> All the importation stations
    --> Trains corresponding to a particular station

    Inputs:
    -------
    --> data,
    -->
    (1) imp_stations = None, return a list of all important stations,
    (2) imp_station = list of particular stations (as per requirement)

    -->
    (1) Only departure = True, returns all the trains that departs from station
    (2) Only departure = False, returns all the trains (i.e. departing + incoming)

    """
        # TODO: mark as deprecable, change notation

    if imp_stations != None:
        imp_stations_list = imp_stations
    else:
        imp_stations_list = get_all_important_station()
    trains_at_stations = get_trains_at_station(trains_dict,important_stations ,only_departue)
    return imp_stations_list, trains_at_stations



def exclusion_list_jtrack():
    station_exclusion_list = ['KO(KS)', 'KO(IC)']

    block_exclusion_list = [    ['"KO", "ST-M", 1114, "(N/A)"'],
                                ['"KO", "ST-M", 1113, "(N/A)"'],
                                ['"KO", "ST-M", 1118, "(N/A)"']
                            ]
    return station_exclusion_list, block_exclusion_list

def non_repeating_pair_for_jswitch():

    non_repeating_pairs =    ['KO', 'KO(STM)']
    non_repeating_singles =  ['KO(IC)', 'KO(KS)']

    return non_repeating_pairs, non_repeating_singles

# Js are from here

def josingle(trains_dict, important_stations,imp_stations = None):

    init_josingle = {}
    imp_stations_list, trains_at_stations = important_trains_and_stations(trains_dict, important_stations,imp_stations,True)

    for s in imp_stations_list:
        for j in trains_at_stations[s]:
            s_prime = subsequent_station(trains_dict[j][1], s)
            if s_prime in imp_stations_list:
                for j_prime in trains_at_stations[s]:
                    if j_prime != j and s == subsequent_station(trains_dict[j_prime][1], s_prime):
                        if (s_prime , s) not in init_josingle.keys():
                            josingle_dict_generate(trains_dict, j, j_prime, s, s_prime, init_josingle)

    return init_josingle

def jtrack_subroutine(trains_dict, s, trains_at_stations, block_exclusion_list, current_blocks, vs):

    for j in trains_at_stations[s]:
        b = blocks_list_4station(trains_dict[j][1], s)
        if b not in block_exclusion_list:
            if b in current_blocks:
                i = current_blocks.index(b)+1
                vs[i].append(j)
            else:
                vs.append([j])
                current_blocks.append(b)

def jtrack(trains_dict,important_stations, imp_stations = None):

    init_jtrack = {}
    imp_stations_list, trains_at_stations = important_trains_and_stations(trains_dict, important_stations, imp_stations, False)
    station_exclusion_list, block_exclusion_list = exclusion_list_jtrack()

    for s in imp_stations_list:
        if s not in station_exclusion_list:
            vs = [[]]
            current_blocks = []
            jtrack_subroutine(trains_dict, s, trains_at_stations, block_exclusion_list, current_blocks, vs)
            if len(vs) != 0:
                init_jtrack[s] = vs
    return jtrack_dict_generation(init_jtrack)


def make_jswitch_dict(data, s, j, jprime, in_switch_sequence_j, in_switch_sequence_jprime, out_switch_sequence_j, out_switch_sequence_jprime, vec_of_pairs, non_repeating_pair):

    if bool( in_switch_sequence_j.intersection( in_switch_sequence_jprime ) ) != False :
        if s != non_repeating_pair[1] :
            vec_of_pairs.append( { j : "in" , jprime : "in" } )
        elif subsequent_station(data, j, non_repeating_pair[0]) != s and subsequent_station(data, jprime, non_repeating_pair[0]) != s:
            vec_of_pairs.append( { j : "in" , jprime : "in" } )


    if bool( in_switch_sequence_j.intersection( out_switch_sequence_jprime ) ) != False :
        if s != non_repeating_pair[1] :
            vec_of_pairs.append( { j : "in" , jprime : "out" } )
        elif subsequent_station(data, j, non_repeating_pair[0]) != s and subsequent_station(data, jprime, s) != non_repeating_pair[0]:
            vec_of_pairs.append( { j : "in" , jprime : "out" } )


    if bool( out_switch_sequence_j.intersection( in_switch_sequence_jprime ) ) != False :
        if s != non_repeating_pair[1] :
            vec_of_pairs.append( { j : "out" , jprime : "in" } )
        elif subsequent_station(data, j, s) != non_repeating_pair[0] and subsequent_station(data, jprime, non_repeating_pair[0]) != s:
            vec_of_pairs.append( { j : "out" , jprime : "in" } )


    if bool( out_switch_sequence_j.intersection( out_switch_sequence_jprime ) ) != False :

        if s != non_repeating_pair[1] :
            vec_of_pairs.append( { j : "out" , jprime : "out" } )
        elif subsequent_station(data, j, s) != non_repeating_pair[0] and subsequent_station(data, jprime, s) != non_repeating_pair[0]:
            vec_of_pairs.append( { j : "out" , jprime : "out" } )




def jswitch(data, data_switch, imp_stations = None):

    jswitch = {}

    imp_stations_list, trains_at_stations = important_trains_and_stations(data, imp_stations, False)
    non_repeating_pair, non_repeating_single =  non_repeating_pair_for_jswitch()
    paths = get_Paths(data)

    for s in imp_stations_list:
        vec_of_pairs = []
        station_block = {j: blocks_list_4station(data, j, s) for j in trains_at_stations[s]}
        blocks_list  = {j: train_time_table(data, j)['path'].tolist() for j in trains_at_stations[s]}

        for j, jprime in itertools.combinations(trains_at_stations[s], 2):
            in_switch_sequence_j = z_in(data_switch, j, s, paths, station_block, blocks_list)
            out_switch_sequence_j = z_out(data_switch, j, s, paths, station_block, blocks_list)
            in_switch_sequence_jprime = z_in(data_switch, jprime, s, paths, station_block, blocks_list)
            out_switch_sequence_jprime = z_out(data_switch, jprime, s, paths, station_block, blocks_list)

            if s not in non_repeating_single:
                make_jswitch_dict(data, s, j, jprime, in_switch_sequence_j, in_switch_sequence_jprime, out_switch_sequence_j, out_switch_sequence_jprime, vec_of_pairs, non_repeating_pair)

        jswitch[s] = vec_of_pairs

    return jswitch



def jd(time_tables_dict, important_stations,imp_stations = None):
    """
        function that creates Jd has to be encoded here
    """
    imp_stations_list, trains_at_stations = important_trains_and_stations(time_tables_dict, important_stations,imp_stations, False)
    
    jd = {}
    for s in imp_stations_list:
        jd[s]={}
        for j in trains_at_stations[s]:
            timetable = time_tables_dict[j][1]
            s2 = subsequent_station(timetable,s)
            if s2 == None:
                continue
            if s2 not in jd[s].keys():
                jd[s][s2] = []
            while j not in flatten(jd[s][s2]):
                i = 0
                v = []
                added = False
                while i < len(jd[s][s2]):
                    path_check = common_path(timetable,time_tables_dict[jd[s][s2][i][0]][1],s,s2)==get_blocks_b2win_station4train(timetable,s,s2)[0]
                    if jd[s][s2][i] != [] and path_check== True:
                        jd[s][s2][i].append(j)
                        added = True
                        i+=1
                    else:
                        i+=1
                if added == False:
                    v.append(j)
                    jd[s][s2].append(v)
    return jd



def jd_depr(data, imp_stations = None):
    """
        function that creates Jd has to be encoded here
    """
    imp_stations_list, trains_at_stations = important_trains_and_stations(data, imp_stations, False)
    jd = {}
    for s in imp_stations_list:
        jd[s]={}
        for j in trains_at_stations[s]:
            s2 = subsequent_station(data,j,s)
            if s2 == None:
                continue
            if s2 not in jd[s].keys():
                jd[s][s2] = []
            while j not in flatten(jd[s][s2]):
                i = 0
                v = []
                added = False
                while i < len(jd[s][s2]):
                    path_check = common_path(data,jd[s][s2][i][0],j,s,s2)==get_blocks_b2win_station4train(data,j,s,s2)[0]
                    if jd[s][s2][i] != [] and path_check== True:
                        jd[s][s2][i].append(j)
                        added = True
                        i+=1
                    else:
                        i+=1
                if added == False:
                    v.append(j)
                    jd[s][s2].append(v)
    return jd

# taus are from here

def get_taus_pass(train_dict,trains = None):
    """Function to generate taus_pass, a dictionary with
    information about passing time for a given train between
    two subsequent stations. It has as key the "train_s1_s2"
    and value minimal passing time between stations for a 
    given train.


    Arguments:
        data -- data file containing train time tables
        data_path_check -- data file containing passing time between blocks

    Keyword Arguments:
        trains -- list of trains (default: {None})

    Returns:
        taus_pass - dictionary with key "train_s1_s2"
        and value minimal_passing_time(train, s1, s2)
    """
    taus_pass = {}
    paths = get_Paths(train_dict)
    if trains == None:
        trains = paths.keys()
    for train in trains:
        timetable = train_dict[train][1]
        for station in paths[train]:
            station2 = subsequent_station(timetable,station)
            if station2 != None:
                taus_pass[f"{train}_{station}_{station2}"] = minimal_passing_time(timetable,station,station2,resolution=1, verbose = True)
    return taus_pass


def get_taus_stop(train_dict,trains = None):
    """Function for getting the mininal stop time for 
    a train in a station. 

    Arguments:
        data -- data file containing train time tables
        data_path_check -- data file containing passing time between blocks

    Keyword Arguments:
        trains -- list of trains (default: {None})

    Returns:
        taus_stop -- Dictionary with keys "train_station"
        and value the minimal_stay(train,station)
    """
    taus_stop = {}
    taus_prep = {}
    first_station = False

    paths = get_Paths(train_dict)
    if trains == None:
        trains = paths.keys()
    for train in trains:
        for i,station in enumerate(paths[train]):
            if i == 0:
                first_station = True
            if (i == len(paths[train])-1) and subsequent_block(train_dict[train][1]["path"].tolist(),blocks_list_4station(train_dict[train][1], station)[0])==None:
                continue
            time_flag,ts_prep = minimal_stay(train,station,train_dict,first_station=first_station)
            taus_stop[f"{train}_{station}"] = time_flag
            taus_prep.update(ts_prep)
    return taus_stop,taus_prep

def get_taus_prep(train_dict):
    """ Function that gives the preparation time
    for a given train at station

    _extended_summary_

    Arguments:
        data -- data with train time tables

    Returns:
        taus_prep -- dictionary with key "train_station"
        and value turn_around_time(train,station)
    """
    taus_prep={}
    paths = get_Paths(train_dict)
    for train,stations in paths.items():
        s = stations[0]
        st_prep = turn_around_time(train_dict[train][1],s,r=1)
        if st_prep != 0:
            taus_prep[f"{train}_{s}"] = st_prep
    return taus_prep


def get_taus_headway(train_dict,important_stations,r=1):
    important_stations_list = list(important_stations.keys())
    jd_dict = jd(train_dict,important_stations)
    taus_headway = {}
    list_of_k1_pairs = {("KO(STM)", 'KZ'), ("CB", "CM"), ("KTC-CB", "via Gt")}
    for station1 in important_stations_list:
        for station2 in jd_dict[station1].keys():
            for train1,train2 in [a for a in it.product(flatten(jd_dict[station1][station2]),repeat=2) if a[0]!= a[1]]:
                blocks_sequence = common_path(train_dict[train1][1],train_dict[train2][1],station1,station2)
                t_pass = np.zeros(len(blocks_sequence))
                deltas_vec = np.zeros(len(blocks_sequence))
                for i in range(len(blocks_sequence)):
                    t = lambda i,train: get_passing_time_block(blocks_sequence[i],train_dict[train][1])
                    t_pass[i]= t(i,train1)
                    if i > 0:
                        deltas_vec[i] = sum([t(j,train1) -t(j,train2) for j in range(i)])
                    k = 2
                    if (station1,station2) in list_of_k1_pairs or (station2,station1) in list_of_k1_pairs:
                        print("print is this happening?: ",station1,station2)
                        k=1
                t_headway = 0
                if len(blocks_sequence) > 0: 
                    t_headway = np.max([np.sum([t_pass[x:x+k]])+ deltas_vec[x] for x in range(len(deltas_vec))])  
                if r==1:
                    t_headway = round(t_headway)
                taus_headway[f"{train1}_{train2}_{station1}_{station2}"] = t_headway
    return taus_headway