from numpy import float32, indices
import pandas as pd
from .utils import common_elements


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



def z_in(data_path_check, j, s, paths, station_blocks, blocks_lists):

    train = j
    in_station = s
    sts = paths[train]
    station_block = station_blocks[j]
    blocks_list = blocks_lists[j]

    for block_list_el_no, block_list_el in enumerate(blocks_list):

        if block_list_el == station_block[0]:
            next_block = blocks_list[block_list_el_no]
            if sts.index(in_station)==0:
                return set()
            else:
                previous_block = blocks_list[block_list_el_no-1]

            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(data_path_check, previous_block, next_block)
            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)

            if len(switch_position) != 0:
                for s in switch_position:
                    switch = data_path_check['switches'][s]
                    if type(switch) is float:
                        switch = eval(str(switch).replace('.', ','))
                        switch = set(switch)
                    else:
                        switch = eval(switch)
                        if type(switch) != int:
                            switch = set(switch)
                        else:
                            switch = set([switch])
            else:
                switch = set()

    return switch



def z_out(data_path_check, j, s, paths, station_blocks, blocks_lists):

    train = j
    out_station = s
    sts = paths[train]
    station_block = station_blocks[j]
    blocks_list = blocks_lists[j]

    for block_list_el_no, block_list_el in enumerate(blocks_list):

        if block_list_el == station_block[0]:
            previous_block = blocks_list[block_list_el_no]
            if sts.index(out_station)==len(sts)-1:
                return set()
            else:
                next_block = blocks_list[block_list_el_no+1]

            list_pos_previous_block, list_pos_next_block = block_indices_to_interprete_switches(data_path_check, previous_block, next_block)
            switch_position = common_elements(list_pos_next_block, list_pos_previous_block)

            if len(switch_position) != 0:
                for s in switch_position:
                    switch =  data_path_check['switches'][s]
                    if type(switch) is float:
                        switch = eval(str(switch).replace('.', ','))
                        switch = set(switch)
                    else:
                        switch = eval(switch)
                        if type(switch) != int:
                            switch = set(switch)
                        else:
                            switch = set([switch])
            else:
                switch = set()

    return switch
