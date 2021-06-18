import pandas as pd
import numpy as np

data = pd.read_csv("../data/train_schedule.csv", sep = ";")

def get_indexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

# convert csv to dictionary
train_dict = {}
for i in range(len(data['Unnamed: 0'])):
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
        train_data = data.iloc[tt_init:pa-1+tt_init].reset_index(drop=True).rename(columns={'Unnamed: 0': 'path'})
        info += [data['Unnamed: 0'][pa-1+tt_init]]
        train_dict[train] = [info,train_data]
print(train_dict)
path_check_data = pd.read_excel("../data/KZ-KO-KL-CB_paths.ods", engine="odf")
