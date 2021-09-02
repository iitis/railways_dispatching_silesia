import numpy as np
import pulp as pus
import itertools
from input_data import *
from helpers_functions import *

def minimal_span(problem, timetable, delay_var, y, train_sets, μ):
    "minimum span condition"


    S = train_sets["Paths"]
    for js in train_sets["Jd"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp):

                s_next = subsequent_station(S, j, s)
                s_nextp = subsequent_station(S, jp, s)

                if (s_next != None and s_next == s_nextp):

                    problem += delay_var[jp][s] + earliest_dep_time(S, timetable, jp, s) + μ*(1-y[j][jp][s]) - delay_var[j][s] - earliest_dep_time(S, timetable, j, s) \
                     >= timetable["tau"]["blocks"][str(j)+"_"+str(s)+"_"+str(s_next)] +\
                        max(0, timetable["tau"]["pass"][str(j)+"_"+str(s)+"_"+str(s_next)] - timetable["tau"]["pass"][str(jp)+"_"+str(s)+"_"+str(s_next)])

                    problem += delay_var[j][s] + earliest_dep_time(S, timetable, j, s) + μ*y[j][jp][s] - delay_var[jp][s] - earliest_dep_time(S, timetable, jp, s) \
                    >= timetable["tau"]["blocks"][str(jp)+"_"+str(s)+"_"+str(s_next)] +\
                     max(0, timetable["tau"]["pass"][str(jp)+"_"+str(s)+"_"+str(s_next)] - timetable["tau"]["pass"][str(j)+"_"+str(s)+"_"+str(s_next)])


def single_line(problem, timetable, delay_var, y, train_sets, μ):
    "minimum span condition"

    S = train_sets["Paths"]
    for js in train_sets["Josingle"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp)[0:-1]:

                s_previous = previous_station(S, j, s)
                s_previousp = previous_station(S, jp, s)

                if s_previousp != None:
                    print(jp, s, s_previousp)
                    problem += delay_var[j][s] + earliest_dep_time(S, timetable, j, s) + μ*(1-y[j][jp][s])  \
                     >= delay_var[jp][s_previousp] + earliest_dep_time(S, timetable, jp, s_previousp) +\
                    timetable["tau"]["pass"][str(jp)+"_"+str(s_previousp)+"_"+str(s)] + timetable["tau"]["res"]

                    problem += delay_var[jp][s_previousp] + earliest_dep_time(S, timetable, jp, s_previousp) + μ*y[j][jp][s] \
                     >= delay_var[j][s] + earliest_dep_time(S, timetable, j, s) +\
                    timetable["tau"]["pass"][str(j)+"_"+str(s)+"_"+str(s_previousp)] + timetable["tau"]["res"]


def minimal_stay(problem, timetable, delay_var, train_sets):

    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]
    "minimum stay condition"
    for j in train_sets["J"]:
        for s in S[j]:

            s_previous = previous_station(S, j, s)

            if (s_previous != None and s != not_considered_station[j]):
                problem += delay_var[j][s]  >= delay_var[j][s_previous]



def track_occuparion(problem, timetable, delay_var, y, train_sets, μ):
    "track occupation"

    S = train_sets["Paths"]
    for s in train_sets["Jtrack"].keys():
        js = train_sets["Jtrack"][s]
        for (j,jp) in itertools.combinations(js, 2):

            s_previous = previous_station(S, j, s)
            s_previousp = previous_station(S, jp, s)

            # the last condition is to keep an order if trains are folowwing one another
            if (s_previous == s_previousp and s_previous != None and occurs_as_pair(j, jp, train_sets["Jd"])):

                problem += y[j][jp][s] == y[j][jp][s_previous]

            if s_previousp != None:

                problem += delay_var[jp][s_previousp] + earliest_dep_time(S, timetable, jp, s_previousp)+ \
                    timetable["tau"]["pass"][str(jp)+"_"+str(s_previousp)+"_"+str(s)] + μ*(1-y[j][jp][s]) >= \
                    delay_var[j][s] + earliest_dep_time(S, timetable, j, s) + timetable["tau"]["res"]

            if s_previous != None:

                problem += delay_var[j][s_previous] + earliest_dep_time(S, timetable, j, s_previous) +\
                    timetable["tau"]["pass"][str(j)+"_"+str(s_previous)+"_"+str(s)] + μ*y[j][jp][s] >= \
                    delay_var[jp][s] + earliest_dep_time(S, timetable, jp, s) + timetable["tau"]["res"]



def objective(problem, timetable, delay_var, train_sets, d_max):
    "objective function"

    S = train_sets["Paths"]
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(i, j)/d_max for i in train_sets["J"] for j in S[i] if penalty_weights(i,j) !=0])


def return_delay_time(S, timetable, prob, j, s):

    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            delay = v.varValue
            time = v.varValue + earliest_dep_time(S, timetable, j, s)
            return delay, time
    return 0, 0

def impact_to_objective(prob, timetable, j,s, d_max):
    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            return penalty_weights(j,s)/d_max*v.varValue
    return 0.




def linear_varibles(train_sets, d_max):

    S = train_sets["Paths"]

    trains_inds = train_sets["J"]

    secondary_delays_var = dict()

    for train in train_sets["J"]:

        secondary_delays_var.update(pus.LpVariable.dicts("Delays", ([train], S[train]), 0, d_max, cat='Integer'))


    y = dict()

    all_trains = np.concatenate([train_sets["Josingle"], train_sets["Jd"]])


    for js in all_trains:
        train1 = []
        train2 = []
        no_station = []
        for pair in itertools.combinations(js, 2):
            train1.append(pair[0])
            train2.append(pair[1])

            no_station = common_path(S, pair[0], pair[1])[0:-1]
        if len(js) > 1:

            y1 = pus.LpVariable.dicts("y", (train1, train2, no_station), 0, 1, cat='Integer')

            update_dictofdicts(y, y1)

    for s in train_sets["Jtrack"].keys():

        for pair in itertools.combinations(train_sets["Jtrack"][s], 2):

            y1 = pus.LpVariable.dicts("y", ([pair[0]], [pair[1]], [s]), 0, 1, cat='Integer')

            update_dictofdicts(y, y1)

    return secondary_delays_var, y



def solve_linear_problem(train_sets, timetable_input, d_max, μ):

    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var, y = linear_varibles(train_sets, d_max)


    minimal_span(prob, timetable_input, secondary_delays_var, y, train_sets, μ)
    minimal_stay(prob, timetable_input, secondary_delays_var, train_sets)
    single_line(prob, timetable_input, secondary_delays_var, y, train_sets, μ)

    track_occuparion(prob, timetable_input, secondary_delays_var, y, train_sets, μ)

    objective(prob, timetable_input, secondary_delays_var, train_sets, d_max)

    prob.solve()

    return prob


if __name__ == "__main__":
    d_max = 10
    μ = 30

    timetable_input = small_timetable()

    train_sets = {
    "skip_station": {
        0: [None],
        1: [None],
        2: [0],
    },
    "Paths": {0: [0,1], 1: [0,1], 2: [1,0]},
    "J": [0,1,2],
    "Jd": [],
    "Josingle": [[1,2], []],
    "Jround": dict(),
    "Jtrack": {1: [0,1]},
    "Jswitch": dict()
    }



    solve_linear_problem(train_sets, timetable_input, d_max, μ)
