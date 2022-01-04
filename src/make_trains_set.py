from re import VERBOSE
from time_table_check import *
import pandas as pd
from utils import *

def josingle():

    josingle = {}

    trains_at_stations = get_trains_depart_from_station()

    for s in get_all_important_station():

        for j in trains_at_stations[s]:

            s_prime = subsequent_station(j, s)

            if s_prime != None:

                for j_prime in trains_at_stations[s]:

                    if j_prime != j:

                        s = subsequent_station(j_prime, s_prime)
    #                     print(f'{j} goes {s}->{s_prime} while {j_prime} goes {s_prime}->{s}')

                        if s != None:

                            path = get_blocks_b2win_station4train(j, s, s_prime, verbose = False)[0]
                            path_j_prime = get_blocks_b2win_station4train(j_prime, s_prime, s, verbose = False)[0]

                            if len(path) != 0 and path == list(reversed(path_j_prime)):

                                if (s,s_prime) or (s_prime,s) not in josingle.keys():

                                    josingle[(s,s_prime)] = [j, j_prime]

                                else:

                                    josingle[(s,s_prime)].append([j, j_prime])


                            elif len(list(set(path).intersection(path_j_prime))) != 0:

                                print('assertion error "partial common path is not supported')

    return josingle


if __name__ == "__main__":

    data = pd.read_csv("../data/train_schedule.csv", sep = ";")

    print(josingle())
    # k = {('1', '2'):[3, 1], ('2', '1'): [1, 3]}

    # for keys1 in k.keys():
    #     for keys2 in k.keys():

    #         if keys1 != keys2:

    #             print(keys1, keys2)
