import functools as ft
from datetime import datetime
import pandas as pd

from .make_J_taus import get_trains_pair9
from .utils import flatten
from .time_table_check import train_important_stations


def get_schedule_per_train(timetable):
    """ Return a dictionary with initial scheduling for a given train.
        It take as keys trains with their important stations. 
        
    Arguments:
        timetable -- time table of the train (pandas.DataFrame)

    Returns:
        Dict with keys "station" and value "Dep" if exists
    """

    timetable = timetable[
        timetable["important_station"].notnull() & timetable["Dep"].notnull()
    ]
    return {
        station: timetable[timetable["important_station"] == station]["Dep"].values[0]
        for station in timetable["important_station"]
    }


def get_schedule(train_dicts:dict, t1:str):
    """_summary_

    Arguments:
        train_dicts -- _description_
        t1 -- _description_

    Returns:
        _description_
    """
    
    t1 = str(t1)
    schedule = {}

    for train in train_dicts.keys():
        timetable = train_dicts[train][1]
        times_4_trains = get_schedule_per_train(timetable)
        for station in times_4_trains.keys():
            t2 = times_4_trains[station]
            time = calc_time_diff(t1, t2)
            schedule[f"{train}_{station}"] = time
    return schedule


def calc_time_diff(t1, t2, format="default"):
    if format == "default":
        format = "%H:%M"
    t1, t2 = str(t1), str(t2)
    t1, t2 = datetime.strptime(t1, format), datetime.strptime(t2, format)
    time = ft.reduce(lambda a, b: b - a, sorted([t1, t2])).total_seconds() / 60
    if t1 > t2:
        time *= -1
    return time


def get_initial_conditions(train_dicts, t1):
    t1 = str(t1)
    initial_conditions = {}
    for train in train_dicts.keys():
        timetable = train_dicts[train][1]
        timetable = (
            timetable[timetable["important_station"].notnull()].fillna(0).iloc[0]
        )
        station = timetable["important_station"]
        t2 = timetable["Dep"]
        if t2 == 0:
            t2 = timetable["Approx_enter"]
        if t2 == 0:
            time = 0
        else:
            time = calc_time_diff(t1, t2)
        initial_conditions[f"{train}_{station}"] = time
    return initial_conditions


def add_delay(initial_conditions, train, delay):
    t_string = str(train) + "_"
    new_value = {
        key: value + delay
        for key, value in initial_conditions.items()
        if t_string in key
    }
    new_conditions = initial_conditions.copy()
    new_conditions.update(new_value)
    return new_conditions


def make_weights(train_dict, stopping=1, fast=1.5, express=1.75, empty=0):
    company_weights = {
        "KS - OsP": stopping,
        "IC - EIP": express,
        "PR - R": stopping,
        "IC - TLK": fast,
        "KS - Os": stopping,
        "IC - IC": fast,
    }

    penalty_weights = {
        f"{train}_{train_important_stations(train_dict[train][1])[-2]}": company_weights[
            train_dict[train][0][0]
        ]
        for train in train_dict.keys()
    }
    penalty_weights.update(
        {
            f"{train}_{train_important_stations(train_dict[train][1])[-2]}": empty
            for train in [
                x
                for x in train_dict.keys()
                if x // 10 in flatten(get_trains_pair9(train_dict))
            ]
        }
    )

    return penalty_weights
