#!/usr/bin/env python3

import sys
import pickle
import railway_lines as rl

"""
with open('cqm5_case3_Integer'.pkl, 'rb') as ifi:
    data = pickle.load(ifi)

lists = []
for k1 in data.keys():
    for k2 in data[k1].keys():
        lists.append(tuple(data[k1][k2].keys()))
routes = sorted(list(set(lists)))
"""

#Generic
line = rl.RAILWAYSEGMENTS['137138GLYKZ']
stations = [(s['callsign'], s['km']) for s in line if s['callsign'] != '']
xrange = (stations[0][1], stations[-1][1])
print("set xrange [%f:%f]"%xrange)
ticsstring = 'set xtics ('
for station in stations:
    ticsstring += '"%s" %f,'%station
ticsstring = ticsstring[:-1]+')'
print(ticsstring)

print("set grid")



print('plot x')
print('pause -1')
