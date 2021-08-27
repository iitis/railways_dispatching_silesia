import numpy as np
import pulp as pus
import itertools
from input_data import penalty_weights
from helpers_functions import *

def minimal_span(problem, delay_var, y, S, train_sets, μ):
    "minimum span condition"
    for js in train_sets["Jd"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp):

                s_next = subsequent_station(S, j, s)
                s_nextp = subsequent_station(S, jp, s)

                if (s_next != None and s_next == s_nextp):

                    problem += delay_var[jp][s] + earliest_dep_time(S, jp, s) + μ*(1-y[j][jp][s]) - delay_var[j][s] - earliest_dep_time(S, j, s) \
                     >= tau('blocks', j, s, s_next) + max(0, tau('pass', j, s, s_next) - tau('pass', jp, s, s_next))

                    problem += delay_var[j][s] + earliest_dep_time(S, j, s) + μ*y[j][jp][s] - delay_var[jp][s] - earliest_dep_time(S, jp, s) \
                    >= tau('blocks', jp, s, s_next) + max(0, tau('pass', jp, s, s_next) - tau('pass', j, s, s_next))


def single_line(problem, delay_var, y, S, train_sets, μ):
    "minimum span condition"
    for js in train_sets["Josingle"]:
        for (j,jp) in itertools.combinations(js, 2):
            for s in common_path(S, j, jp)[0:-1]:

                s_previous = previous_station(S, j, s)
                s_previousp = previous_station(S, jp, s)

                if s_previousp != None:

                    problem += delay_var[j][s] + earliest_dep_time(S, j, s) + μ*(1-y[j][jp][s])  \
                     >= delay_var[jp][s_previousp] + earliest_dep_time(S, jp, s_previousp) + tau('pass', jp, s_previousp , s) + tau('res', jp, j , s)

                    problem += delay_var[jp][s_previousp] + earliest_dep_time(S, jp, s_previousp) + μ*y[j][jp][s] \
                     >= delay_var[j][s] + earliest_dep_time(S, j, s) + tau('pass', j, s, s_previousp) + tau('res', j, jp , s)


def minimal_stay(problem, delay_var, S, train_sets, not_considered_station):
    "minimum stay condition"
    for j in train_sets["J"]:
        for s in S[j]:

            s_previous = previous_station(S, j, s)

            if (s_previous != None and s != not_considered_station[j]):
                problem += delay_var[j][s]  >= delay_var[j][s_previous]



def track_occuparion(problem, delay_var, y, S, train_sets, μ):
    "track occupation"
    for s in train_sets["Jtrack"].keys():
        js = train_sets["Jtrack"][s]
        for (j,jp) in itertools.combinations(js, 2):

            s_previous = previous_station(S, j, s)
            s_previousp = previous_station(S, jp, s)

            # the last condition is to keep an order if trains are folowwing one another
            if (s_previous == s_previousp and s_previous != None and occurs_as_pair(j, jp, train_sets["Jd"])):

                problem += y[j][jp][s] == y[j][jp][s_previous]

            if s_previousp != None:

                problem += delay_var[jp][s_previousp] + earliest_dep_time(S, jp, s_previousp)  + tau("pass", jp, s_previousp, s) + μ*(1-y[j][jp][s]) >= \
                 delay_var[j][s] + earliest_dep_time(S, j, s) + tau('res')

            if s_previous != None:

                problem += delay_var[j][s_previous] + earliest_dep_time(S, j, s_previous) + tau("pass", j, s_previous, s) + μ*y[j][jp][s] >= \
                     delay_var[jp][s] + earliest_dep_time(S, jp, s) + tau('res')



def objective(problem, delay_var, S, train_sets, d_max):
    "objective function"
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(i, j)/d_max for i in train_sets["J"] for j in S[i] if penalty_weights(i,j) !=0])


def return_delay_time(S, prob, j, s):

    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            delay = v.varValue
            time = v.varValue + earliest_dep_time(S, j, s)
            return delay, time
    return 0, 0

def impact_to_objective(prob, j,s, d_max):
    for v in prob.variables():
        if v.name == "Delays_"+str(j)+"_"+str(s):
            return penalty_weights(j,s)/d_max*v.varValue
    return 0.




def linear_varibles(train_sets, S, d_max):

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



def solve_linear_problem(train_sets, S, d_max, μ, not_considered_station):

    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var, y = linear_varibles(train_sets, S, d_max)


    minimal_span(prob, secondary_delays_var, y, S, train_sets, μ)
    minimal_stay(prob, secondary_delays_var, S, train_sets, not_considered_station)
    single_line(prob, secondary_delays_var, y, S, train_sets, μ)

    track_occuparion(prob, secondary_delays_var, y, S, train_sets, μ)

    objective(prob, secondary_delays_var, S, train_sets, d_max)

    prob.solve()

    return prob
