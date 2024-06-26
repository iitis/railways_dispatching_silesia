import functools as ft
from datetime import datetime
import pandas as pd

from .make_J_taus import get_trains_pair9
from .utils import flatten
from .time_table_check import train_important_stations


def get_schedule_per_train(timetable):
    """Return a dictionary with initial scheduling for a given train.
        It take as keys the train important stations.

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


def get_schedule(train_dicts: dict, t1: str):
    """Returns a dictionary with scheduling for a set of trains.

    Arguments:
        train_dicts -- Dict containing all the trains with their timetables
        t1 -- Initial time for comparison.

    Returns:
        scheduling -- Dict with keys as train_station and value the time diference between
                      t1 and their scheduled Departure (if exists) or Arpoximate Departure.
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


def make_weights(
    train_dict, skip_stations, stopping=1, fast=1.5, express=1.75, empty=0
):
    trains_weights = {
        "KS - Os": stopping,
        "PR - R": stopping,
        "KS - OsP": stopping,  # TODO we may make it semi fast
        "IC - TLK": fast,
        "IC - IC": fast,
        "IC - EIP": express,
        "IC - EIC": express,
    }

    penalty_weights = {}
    for train in train_dict.keys():
        type_of_train = train_dict[train][0][0]
        weight = trains_weights[type_of_train]
        if train // 10 in flatten(get_trains_pair9(train_dict)):
            weight = empty
        station = train_important_stations(train_dict[train][1])[-1]
        if train in skip_stations and station == skip_stations[train]:
            station = train_important_stations(train_dict[train][1])[-2]

        penalty_weights.update({f"{train}_{station}": weight})

    return penalty_weights
