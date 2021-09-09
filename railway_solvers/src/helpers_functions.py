import numpy as np
#####   functions ####


def occurs_as_pair(a,b, vecofvec):
    "check whether a and b occurs together in the same vector of the vector of vectors"
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False

def update_dictofdicts(d1, d2):
    "update d1 (dict of dict of dict ...) by one element d2 (dict of dict of dict ...)"

    assert np.size(d2.keys()) == 1

    for k in d2.keys():
        if k in d1.keys():
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1



def subsequent_station(path, s):
    "given a train path and atation returns next station in this path"
    k = path.index(s)
    if k == len(path)-1:
        return None
    else:
        return path[k+1]

def previous_station(path, s):
    "given a train path and atation returns preceeding station in this path"
    k = path.index(s)
    if k == 0:
        return None
    else:
        return path[k-1]


def common_path(S, j, jp):
    "returns a common path of 2 trains"
    return [s for s in S[j] if s in S[jp]]


def tau(timetable, key, train = None, first_station = None, second_station = None):
     "from timetable return particular τs values, for given train and station/stations"
     if key == "pass" or key == "blocks" or key == "stop":
         return timetable["tau"][key][str(train)+"_"+str(first_station)+"_"+str(second_station)]
     elif key == "res":
         return timetable["tau"]["res"]
     return None


def initial_conditions(timetable, train, station):
    "given a timetable returns initial condistions (input data) for chosen trains subset"
    return timetable["initial_conditions"][str(train)+"_"+str(station)]



def penalty_weights(timetable, train, station):
    "from a timetable returns penalty weight for a given train at a given station"
    try:
        return timetable["penalty_weights"][str(train)+"_"+str(station)]
    except:
        return 0.


def earliest_dep_time(S, timetable, train, station):
    "returns earlies possible departure of a train from the given station"
    # this is to ensure train can not leave befire tche schedule, if schedule is given
    if "schedule" in timetable:
        sched = timetable["schedule"][str(train)+"_"+str(station)]
    else:
        sched = -np.inf
    try:
        return np.maximum(sched, initial_conditions(timetable, train, station))
    except:
        s = previous_station(S[train], station)
        tau_pass = tau(timetable, "pass", train, s, station)
        tau_stop = tau(timetable, "stop", train, station)

        return np.maximum(sched, earliest_dep_time(S, timetable, train, s) + tau_pass + tau_stop)
