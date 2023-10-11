import datetime
import pandas as pd

class TrainPath:
    def __init__(self):
        self.number = None
        self.status = None
        self.route = None
        self.path = None
    def __repr__(self):
        return str(self.number) + ' / ' + self.status +'\n'+ str(pd.DataFrame(self.path))
    def __str__(self):
        return str(self.number) + ' / ' + self.status + '\n'+ str(pd.DataFrame(self.path))

def arrival_for_sort(x):
    try:
        arrival = x['arrive']
    except KeyError:
        arrival = datetime.datetime(1899, 1, 1, 0, 0)
    return arrival

def none_if_not(x,key):
    try:
        result = x[key]
    except KeyError:
        result = None
    return(result)

def kdtrain2trainpath(trainNumber, kdtrain, status='resolved'):
    "Convert native train data to a train path"
    train = TrainPath()
    train.status = status
    train.number = str(trainNumber)
    train.status = status
    #NB: it is stored as a dict, but we want it as an ordered list
    route_temp = [(k, v) for k,v in kdtrain.items()]
    train.route = [x[0] for x in sorted(
        [(x[0], arrival_for_sort(
            x[1])) for x in [
            x for x in route_temp]], key=lambda x: x[1])]
    if status == 'conflicted':
        prefix = 'conflicted_'
    else:
        prefix = ''
    train.path = [{'station':k,\
                       'arrival':none_if_not(kdtrain[k], prefix+ 'arrive'),\
                       'departure':none_if_not(kdtrain[k], 'departure')}\
                      for k in train.route]
    return train
