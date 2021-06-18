import pandas as pd
import numpy as np

data = pd.read_csv("data/train_schedule.csv", sep = ";")

train_dict = {}
for i in range(40):
    if data['Unnamed: 0'][i].isnumeric():
        info = []
        train = data['Unnamed: 0'][i]
        info += [data['Unnamed: 0'][i-1]]
        info += [data['Unnamed: 0'][i+x] for x in range(1,3)]
    statment = data['Unnamed: 0'][i][0:4]
    if statment in ['from','depa']:
        tt_init = i+1
        tt_item = data['Unnamed: 0'][i+1]
        pa = 1
        while tt_item[0:2] not in ['to','te']:
            pa+=1
            tt_item = data['Unnamed: 0'][i+pa]
        train_data = data.iloc[tt_init:pa-1+tt_init]
        info += [data['Unnamed: 0'][pa-1+tt_init]]
        train_dict[train] = [info,train_data]
