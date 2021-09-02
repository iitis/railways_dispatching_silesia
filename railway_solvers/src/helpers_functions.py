from input_data import initial_conditions, tau

#####   functions ####


def occurs_as_pair(a,b, vecofvec):
    for v in vecofvec:
        if (a in v and b in v) and a != b:
            return True
    return False



def subsequent_station(S, j, s):
    path = S[j]
    k = path.index(s)
    if k == len(path)-1:
        return None
    else:
        return path[k+1]

def previous_station(S, j, s):
    path = S[j]

    k = path.index(s)

    if k == 0:
        return None
    else:
        return path[k-1]


def common_path(S, j, jp):
    return [s for s in S[j] if s in S[jp]]

def update_dictofdicts(d1, d2):
    k1 = d1.keys()
    k2 = d2.keys()
    for k in k2:
        if k in k1:
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1


def earliest_dep_time(S, timetable, train = None, station = None):

    t = initial_conditions(train, station)
    if t >= 0:
        return t
    else:
        s = previous_station(S, train, station)
        tau_pass = timetable["tau"]["pass"][str(train)+"_"+str(s)+"_"+str(station)]
        tau_stop = timetable["tau"]["stop"][str(train)+"_"+str(station)+"_none"]
        return earliest_dep_time(S, timetable, train, s) + tau_pass  + tau_stop
