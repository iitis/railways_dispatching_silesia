from numpy import float32, indices
import pandas as pd
from utils import *
from time_table_check import *



def block_indices_to_interprete_switches(data_path_check, previous_block, next_block):

    i = 0
    j = 0
    list_pos_previous_block = []
    list_pos_next_block = []
    for el in data_path_check['previous_block']:
        if el == previous_block:
            list_pos_previous_block.append(i)
        if el == next_block:
            list_pos_next_block.append(i)
        i+= 1

    for el in data_path_check['next_block']:
        if el == previous_block:
            list_pos_previous_block.append(j)
        if el == next_block:
            list_pos_next_block.append(j)
        j+= 1

    return list_pos_previous_block, list_pos_next_block



def z_in(data, data_path_check, j, s):

    train = j
    in_station = s
    station_block = blocks_list_4station(data, train, in_station)
    blocks_list = train_time_table(data, train)['path'].tolist()
    sts = get_Paths(data)[train]

    for block_list_el_no, block_list_el in enumerate(blocks_list):

        if block_list_el == station_block[0]:
            next_block = blocks_list[block_list_el_no]
            if sts.index(in_station)==0:
                print('this is first station')
                return []
            else:
                previous_block = blocks_list[block_list_el_no-1]
            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(data_path_check, previous_block, next_block)
            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)

            for s in switch_position:
                switch = data_path_check['switches'][s]
                if type(switch) is float:
                    switch = eval(str(switch).replace('.', ','))
                    switch = list(switch)
                else:
                    switch = '[' + ','.join([switch]) + ']'

    return switch



def z_out(data, data_path_check, j, s):

    train = j
    out_station = s
    station_block = blocks_list_4station(data, train, out_station)
    blocks_list = train_time_table(data, train)['path'].tolist()
    sts = get_Paths(data)[train]

    for block_list_el_no, block_list_el in enumerate(blocks_list):
        if block_list_el == station_block[0]:
            previous_block = blocks_list[block_list_el_no]
            if sts.index(out_station)==len(sts)-1:
                print('this is last station')
                return []
            else:
                next_block = blocks_list[block_list_el_no+1]

            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(data_path_check, previous_block, next_block)
            # print(list_pos_next_block, list_pos_previous_block)
            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)
            for s in switch_position:
                switch =  data_path_check['switches'][s]
                if type(switch) is float:
                    switch = eval(str(switch).replace('.', ','))
                    switch = list(switch)
                else:
                    switch = '[' + ','.join([switch]) + ']'



    return switch



if __name__ == "__main__":
    j = 44862
    s1 = 'KO'
    s2 = 'KO(STM)'
    print(j, s1)
    print('-------')
    print(z_in(data, j, s1))
    print(z_out(data, j, s1))
    print()
    print(j, s2)
    print('-------')
    print(z_in(data, j, s2))
    print(z_out(data, j, s2))
