from numpy import indices
import pandas as pd
from utils import *

path_to_data = "../data/train_schedule.csv"
data_path_check = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
data = pd.read_csv(path_to_data, sep = ";")


def block_indices_to_interprete_switches(previous_block, next_block):

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



def z_in(data, j, s):

    train = j
    in_station = s
    station_block = blocks_list_4station(data, train, in_station)
    blocks_list = train_time_table(data, train)['path'].tolist()
    sts = get_Paths(data)[train]

    for block_list_el_no, block_list_el in enumerate(blocks_list):
        
        if block_list_el == station_block[0]:
            previous_block = blocks_list[block_list_el_no-1] 
            if sts.index(in_station)==len(sts)-1:
                return []
            else:
                next_block = blocks_list[block_list_el_no]
            
            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(previous_block, next_block)
            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)
            
            for s in switch_position:
                switch = data_path_check['switches'][s]

    return switch

        

def z_out(data, j, s):

    train = j
    out_station = s
    station_block = blocks_list_4station(data, train, out_station)
    blocks_list = train_time_table(data, train)['path'].tolist()
    sts = get_Paths(data)[train]

    for block_list_el_no, block_list_el in enumerate(blocks_list):
        if block_list_el == station_block[0]:
            previous_block = blocks_list[block_list_el_no]
            if sts.index(out_station)==len(sts)-1:
                return []
            else:
                next_block = blocks_list[block_list_el_no+1]

            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(previous_block, next_block)

            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)
            for s in switch_position:
                switch =  data_path_check['switches'][s]
        
    return switch


if __name__ == "__main__":

    j = 94766
    s1 = 'KO'
    s2 = 'KO(STM)'
    print(z_in(data, j, s1))
    print(z_out(data, j, s1))
    print('----------')
    print(z_in(data, j, s2))
    print(z_out(data, j, s2))
