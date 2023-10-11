#!/usr/bin/env python3

import sys
import pickle
import railway_lines as rl
import train_utils as tu

with open(sys.argv[1], 'rb') as ifi:
    data = pickle.load(ifi)

lists = []
for k1 in data.keys():
    for k2 in data[k1].keys():
        lists.append(tuple(data[k1][k2].keys()))
routes = sorted(list(set(lists)))

def quantum_train_route(train):
    return list(train.keys())

if 'cqm' in sys.argv[1]:
    kdtraindata = data[int(sys.argv[2])]
else:
    kdtraindata = data
    
for trainno in kdtraindata.keys():
    for status in ('conflcted', 'resolved'):
        t = tu.kdtrain2trainpath(trainno, kdtraindata[trainno], status=status)
        print(t)
    print('----------------------------------------')

