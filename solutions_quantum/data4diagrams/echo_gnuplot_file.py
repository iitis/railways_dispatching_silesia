#!/usr/bin/env python3

import sys
import pickle
import argparse
import railway_lines as rl
import train_utils as tu

parser = argparse.ArgumentParser("Echo a train path diagram gnuplot script") 

parser.add_argument('--segment',
                    choices=list(rl.RAILWAYSEGMENTS.keys()),
                    help="Railway segment to display, default: '137138GLYKZ'",
                    default='137138GLYKZ')

parser.add_argument('--fixedtrains',
                    type=str,
                    help='A comma-separated list of train numbers to include anyway, e.g. 44862,44717')

parser.add_argument('--realisation',
                    type=int,
                    help='Realisation number of quantum instances, defaults to 1',
                    default=1)

parser.add_argument('infile',
                    type=str,
                    help='Input file')

ARGS = parser.parse_args()

if ARGS.fixedtrains:
    FIXEDTRAINS = set(ARGS.fixedtrains.strip().split(','))
else:
    FIXEDTRAINS=set([])

with open(ARGS.infile, 'rb') as ifi:
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

def echo_gnuplot_train_labels(train, segment):
    prev_km = None
    for s in train.path:
        try:
            km = rl.station2km(s['station'], segment)
            if s['arrival'] is not None and prev_km is not None:
                label_km = prev_km + ((km - prev_km) /2)
                label_t = (prev_t +(s['arrival'] - prev_t) / 2).strftime('%H:%M')
                print("%f %s %s"%(label_km,label_t, train.number))
            if s['departure'] is not None:
                prev_km = km
                prev_t = s['departure']
        except ValueError:
            pass

        
if 'cqm' in ARGS.infile:
    try:
        kdtraindata = data[ARGS.realisation]
    except:
        kdtraindata = data[int(1)]
else:
    kdtraindata = data



print('set ydata time')
print('set timefmt "%H:%M"')
print('set format y "%H:%M"')
lineno = 0
print('set yrange [*:*] reverse')

print("set title '%s %s'"%(ARGS.segment, sys.argv[1].replace('_','-')))
stations = [(s['callsign'], s['km']) for s in rl.RAILWAYSEGMENTS[ARGS.segment] if s['callsign'] != '']
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
        if rl.train_on_segment(train, ARGS.segment, exceptions=EXCEPTIONS)>=2 or str(trainno) in FIXEDTRAINS:
            print('$trainpath%d << EOD'%lineno)
            echo_gnuplot_train(train, ARGS.segment)
            print('EOD')
            print('$trainpathlabels%d << EOD'%lineno)
            echo_gnuplot_train_labels(train, ARGS.segment)
            print('EOD')
            #print('%s $trainpath%d using 1:2 with lines notitle ls %d, $trainpath%d u 1:2:3 with labels font "Times,8" notitle'%(plotstring, lineno, ls, lineno))
            print('%s $trainpath%d using 1:2 with lines notitle ls %d'%(plotstring, lineno, ls))
            plotstring = 'replot'
            print('%s $trainpathlabels%d using 1:2:3 with labels font "Times,8" notitle'%(plotstring, lineno))
            lineno += 1

        #print('pause 2')
print('pause -1')
