import numpy as np


def occurs_as_pair(a, b, vecofvec):
    """checks whether a and b occurs together in the same vector of vectors """
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False


def update_dictofdicts(d1, d2):
    """updates d1 (nested dict of dict ...)
    by d2 -nested dict of dict ... (with the same structure but single element)
    update at the lowest possible level of nesting
    """
    assert np.size(d2.keys()) == 1

    for k in d2.keys():
        if k in d1.keys():
            update_dictofdicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1


def subsequent_station(path, s):
    """given a train path and atation returns next station in this path"""
    k = path.index(s)
    if k == len(path) - 1:
        return None
    else:
        return path[k + 1]


def previous_station(path, s):
    """given a train path and station s
    returns preceeding station in the path

    if there is no preceeding station returns None
    """
    k = path.index(s)
    if k == 0:
        return None
    else:
        return path[k - 1]


# timetable input is extected to be in the following form of dict of dicts
#  taus are given as
# taus = {"pass" : {"j_s_si" : τ^pass(j,s,s1), ...},
# "blocks" : {"j_j1_s_s1" : τ^pass(j,j1,s,s1)  .... },
# "stop": {"j_s_None" : τ^stop(j,s)}, "res": τ^res}
# τ^res is just one for all situations, it may need to be extended

# train schedule if available (train can not leave before schedule)
# schedule = {"j_s" : t_schedule(j,s_out), ... }

# timetable = {"tau": taus, "schedule" : schedule,
#              "initial_conditions" : {"j_s" : t(j,s_out), ...},
#              "penalty_weights" : {"j_s" : w(j,s), ...}}


def tau(
    timetable,
    key,
    first_train=None,
    first_station=None,
    second_station=None,
    second_train=None,
):
    """given the timetable and the key returns particular time span τ(key)
    for given train and station or stations

    in the key is not in ["blocks", "pass", "stop", "prep", "res"]
    return None
    """
    if key == "blocks":
        return timetable["tau"]["blocks"][
            f"{first_train}_{second_train}_{first_station}_{second_station}"
        ]
    elif key == "pass":
        string = f"{first_train}_{first_station}_{second_station}"
        return timetable["tau"][key][string]
    elif key == "stop":
        return timetable["tau"][key][f"{first_train}_{first_station}"]
    elif key == "prep":
        return timetable["tau"][key][f"{first_train}_{first_station}"]
    elif key == "res":
        return timetable["tau"]["res"]
    return None


def penalty_weights(timetable, train, station):
    """given timetable returns penalty weight for
    a delay above unaviodable at the given station"""

    train_station = f"{train}_{station}"
    if train_station in timetable["penalty_weights"]:
        return timetable["penalty_weights"][train_station]
    else:
        return 0.


def earliest_dep_time(S, timetable, train, station):
    """returns earlies possible departure of a train from the given station
    including unavoidlable delays and the schedule if the schedule is given
    """
    if "schedule" in timetable:
        sched = timetable["schedule"][f"{train}_{station}"]
    else:
        sched = -np.inf
    train_station = f"{train}_{station}"

    if train_station in timetable["initial_conditions"]:
        unaviodable = timetable["initial_conditions"][train_station]
        return np.maximum(sched, unaviodable)
    else:
        s = previous_station(S[train], station)
        τ_pass = tau(
            timetable,
            "pass",
            first_train=train,
            first_station=s,
            second_station=station,
        )
        τ_stop = tau(timetable, "stop", first_train=train, first_station=station)
        unavoidable = earliest_dep_time(S, timetable, train, s) + τ_pass
        unavoidable += τ_stop
        return np.maximum(sched, unavoidable)

# helpers for trains set


def not_the_same_rolling_stock(j, jp, train_sets):
    """checks if two trains (j, jp) are not served by the same rolling stock"""
    for s in train_sets["Jround"].keys():
        if occurs_as_pair(j, jp, train_sets["Jround"][s]):
            return False
    return True


def departure_station4switches(s, j, place_of_switch, train_sets):
    """returns the station symbol from which train j departes prior to passing
    the swith at station s
    """
    if place_of_switch[j] == "out":
        return s
    elif place_of_switch[j] == "in":
        S = train_sets["Paths"]
        return previous_station(S[j], s)


def get_μ(LHS, RHS, d_max):
    """computes minimal value of the large number μ for the order variable
    y ∈ [0,1] conditional inequality such that:

      LHS + delay >= RHS + delay - μ y

      The inequality should be checked for y = 0 and always hold for y = 1
      """
    return np.max([RHS + d_max - LHS, 1.0])
