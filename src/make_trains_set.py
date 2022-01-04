from time_table_check import *
import pandas as pd
from utils import *

def josingle(imp_stations = None):

    init_josingle = {}

    if imp_stations != None:
        imp_stations_list = imp_stations
    else:
        imp_stations_list = get_all_important_station()


    trains_at_stations = get_trains_depart_from_station()

    # print(imp_stations_list)

    for s in imp_stations_list:
        
        for j in trains_at_stations[s]:
            
            s_prime = subsequent_station(j, s)
            
            if s_prime != None:
                
                for j_prime in trains_at_stations[s]:
                    
                    if j_prime != j:
                        
                        s = subsequent_station(j_prime, s_prime)

                        if (s_prime , s) in init_josingle.keys():
                            print(s_prime, s)
                            print('the pair has already been added in the previous steps')
                        
                        else:
                        # print(f'{j} goes {s}->{s_prime} while {j_prime} goes {s_prime}->{s}')

                            if s != None:

                                path = get_blocks_b2win_station4train(j, s, s_prime, verbose = False)[0]
                                path_j_prime = get_blocks_b2win_station4train(j_prime, s_prime, s, verbose = False)[0]

                                if len(path) != 0 and path == list(reversed(path_j_prime)):
                                    
                                    if (s,s_prime) in init_josingle.keys():
                                        init_josingle[(s, s_prime)].append([j, j_prime])
                                    else:
                                        init_josingle[(s, s_prime)] = [[j, j_prime]]

                                elif len(list(set(path).intersection(path_j_prime))) != 0:

                                    print('assertion error partial common path is not supported')


    return init_josingle


if __name__ == "__main__":

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")
    
    imp_stations = ['Mi', 'MJ', 'KL']
    print(josingle())