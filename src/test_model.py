#!/usr/bin/env python3
import sys
import os
from argparse import ArgumentParser
import datetime as dt
from copy import deepcopy
import numpy as np
import pulp as pus

sys.path.append(os.path.abspath("./QUBO"))

#unavoidable delay on train 1 tU(j1, s1out), train 2 tU(j2, s1out), and train 3 tU(j3, s2out) (on station 2).

def tau(x, train, first_station, second_station):
    if ((x == 'pass') and (train == 1) and (first_station == 1) and (first_station == 2)):
        time = 4
    elif ((x == 'pass') and (train == 2) and (first_station == 1) and (first_station == 2)):
        time = 8
    elif ((x == 'pass') and (train == 3) and (first_station == 2) and (first_station == 1)):
        time = 8
    elif ((x == 'blocks') and (train == 1) and (first_station == 1) and (first_station == 2)):
        time = 2
    elif ((x == 'blocks') and (train == 2) and (first_station == 1) and (first_station == 2)):
        time = 2
    elif ((x == 'stop') and (train == 1) and (first_station == 1) and (first_station == None)):
        time = 1
    elif ((x == 'stop') and (train == 2) and (first_station == 2) and (first_station == None)):
        time = 1
    elif ((x == 'res') and (train == None) and (first_station == None) and (first_station == None)):
        time = 1
    return time

def minimum_span_condition():
    offset = []
    tau_ms1 = tau('blocks', 1, 1, 2) 
    con1 = max(0, tau('pass', 1, 1, 2) - tau('pass', 2, 1, 2))
    tau_ms2 = tau('blocks', 2, 1, 2) 
    con2 = max(0, tau('pass', 2, 1, 2) - tau('pass', 1, 1, 2))
    return tau_ms1+con1, tau_ms2+con2

print(minimum_span_condition())
    

# for j1 in [1,2,3]:
    # for j2 in [1,2,3]:
        # if j1 != j2:
            # print(j1,j2)
for s1 in [1,2]:
        for s2 in [1,2]:
            if s1 != s2:
                print(s1,s2)
