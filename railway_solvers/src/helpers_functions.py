
#####   functions ####


def occurs_as_pair(a,b, vecofvec):
    "check whether a and b occurs together in the same vector of the vector of vectors"
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False

def update_dictofdicts(d1, d2):
    "update d1 by d2 in such a way that adds elements of d2 either to the outside dictionary or to the inside one if inside keys are the same"
    #TODO check it for more complex
    for k in d2.keys():
        if k in d1.keys():
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1



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


def tau(timetable, x = None, train = None, first_station = None, second_station = None):

     if x == "pass" or x == "blocks" or x == "stop":
         return timetable["tau"][x][str(train)+"_"+str(first_station)+"_"+str(second_station)]
     elif x == "res":
         return timetable["tau"]["res"]
     return None


def initial_conditions(timetable, train, station):
    return timetable["initial_conditions"][str(train)+"_"+str(station)]



def penalty_weights(timetable, train, station):
    try:
        return timetable["penalty_weights"][str(train)+"_"+str(station)]
    except:
        return 0.


def earliest_dep_time(S, timetable, train, station):

    try:
        return initial_conditions(timetable, train, station)
    except:
        s = previous_station(S, train, station)
        tau_pass = tau(timetable, "pass", train, s, station)

        tau_stop = tau(timetable, "stop", train, station)

        return earliest_dep_time(S, timetable, train, s) + tau_pass  + tau_stop




#####   this wil go to tests #######

# print(input_data["tau"]["pass"]["0_0_1"])

# input_data = small_timetable()

# for t in [0,1,2]:
#     for s1 in [0,1]:
#         for s2 in [0,1]:
#             if s1 != s2 and t + s2 != 0 and t + s1 != 2 and t + s2 != 3:
#                 print(t,s1,s2)
