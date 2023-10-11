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

def echo_gnuplot_train(train, segment):
    for s in train.path:
        try:
            km = rl.station2km(s['station'], segment)
            if s['arrival'] is not None:
                print("%f %s"%(km,s['arrival'].strftime('%H:%M')))
            if s['departure'] is not None:
                print("%f %s"%(km,s['departure'].strftime('%H:%M')))
        except ValueError:
            pass
        
if 'cqm' in sys.argv[1]:
    try:
        kdtraindata = data[int(sys.argv[3])]
    except:
        kdtraindata = data[int(1)]
else:
    kdtraindata = data
try:
    segment = sys.argv[2]
except:
    #segment = '138139KZTY'
    segment = '137138GLYKZ'

if segment not in set(rl.RAILWAYSEGMENTS.keys()):
    raise ValueError('Invalid railway network segment specified')

print('set ydata time')
print('set timefmt "%H:%M"')
print('set format y "%H:%M"')
lineno = 0
#print('set yrange ["00:00":"23:59"]')
#segment = '138139KZTY'
segment = '137138GLYKZ'
print("set title '%s %s'"%(segment, sys.argv[1].replace('_','-')))
stations = [(s['callsign'], s['km']) for s in rl.RAILWAYSEGMENTS[segment] if s['callsign'] != '']
xrange = (stations[0][1], stations[-1][1])
print("set xrange [%f:%f]"%xrange)
ticsstring = 'set xtics ('
for station in stations:
    ticsstring += '"%s" %f,'%station
ticsstring = ticsstring[:-1]+')'
print(ticsstring)
print("set grid")
print('set style line 1 lt rgb "green" lw 3')
print('set style line 2 lt rgb "red" lw 1')

plotstring = 'plot'
EXCEPTIONS = ['KO','KO(STM)']
for trainno in kdtraindata.keys():
    for status in ('resolved', 'conflicted'):
        if status == 'conflicted':
            ls = 2
        else:
            ls = 1
        train = tu.kdtrain2trainpath(trainno, kdtraindata[trainno], status=status)
        if rl.train_on_segment(train, segment, exceptions=EXCEPTIONS)>2:
            print('$trainpath%d << EOD'%lineno)
            echo_gnuplot_train(train, segment)
            print('EOD')
            print("%s $trainpath%d using 1:2 with lines notitle ls %d"%(plotstring, lineno, ls))
            plotstring = 'replot'
            lineno += 1

        #print('pause 2')
print('pause -1')
