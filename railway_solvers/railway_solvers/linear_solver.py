import itertools

import pulp as pus

from .helpers_functions import *


def minimal_span(problem, timetable, delay_var, y, train_sets, μ):
    "adds the minimum span condition to the pulp problem"

    S = train_sets["Paths"]
    for js in train_sets["Jd"]:
        for (j, jp) in itertools.combinations(js, 2):
            # the common path without last station is used, TODO think over
            for s in common_path(S, j, jp)[0:-1]:
                s_next = subsequent_station(S[j], s)
                s_nextp = subsequent_station(S[jp], s)

                LHS = delay_var[jp][s]
                LHS += earliest_dep_time(S, timetable, jp, s)
                LHS += μ*(1-y[j][jp][s]) - delay_var[j][s]
                LHS -= earliest_dep_time(S, timetable, j, s)
                RHS = tau(timetable, 'blocks', j, s, s_next)
                RHS += max(0, tau(timetable, 'pass', j, s, s_next) -
                           tau(timetable, 'pass', jp, s, s_next))
                problem += LHS >= RHS

                LHS = delay_var[j][s]
                LHS += earliest_dep_time(S, timetable, j, s)
                LHS += μ*y[j][jp][s]
                LHS -= delay_var[jp][s]
                LHS -= earliest_dep_time(S, timetable, jp, s)
                RHS = tau(timetable, 'blocks', jp, s, s_next)
                RHS += max(0, tau(timetable, 'pass', jp, s, s_next) -
                           tau(timetable, 'pass', j, s, s_next))
                problem += LHS >= RHS


def single_line(problem, timetable, delay_var, y, train_sets, μ):
    " adds single line condition to the pulp problem"
    S = train_sets["Paths"]
    for js in train_sets["Josingle"]:
        for (j, jp) in itertools.combinations(js, 2):
            # the common path without last station is used, TODO think over
            for s in common_path(S, j, jp)[0:-1]:
                s_previous = previous_station(S[j], s)
                s_previousp = previous_station(S[jp], s)
                if s_previousp != None:
                    LHS = delay_var[j][s]
                    LHS += earliest_dep_time(S, timetable, j, s)
                    LHS += μ*(y[j][jp][s])
                    RHS = delay_var[jp][s_previousp]
                    RHS += earliest_dep_time(S, timetable, jp, s_previousp)
                    RHS += tau(timetable, 'pass', jp, s_previousp, s)
                    RHS += tau(timetable, 'res', jp, j, s)
                    problem += LHS >= RHS

                    LHS = delay_var[jp][s_previousp]
                    LHS += earliest_dep_time(S, timetable, jp, s_previousp)
                    LHS += μ*(1-y[j][jp][s])
                    RHS = delay_var[j][s]
                    RHS += earliest_dep_time(S, timetable, j, s)
                    RHS += tau(timetable, 'pass', j, s, s_previousp)
                    RHS += tau(timetable, 'res', j, jp, s)
                    problem += LHS >= RHS


def minimal_stay(problem, timetable, delay_var, train_sets):
    "adds minimum stay condition to the pulp problem"
    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]

    for j in train_sets["J"]:
        for s in S[j]:
            s_previous = previous_station(S[j], s)
            if (s_previous != None and s != not_considered_station[j]):
                problem += delay_var[j][s] >= delay_var[j][s_previous]


def track_occuparion(problem, timetable, delay_var, y, train_sets, μ):
    "adds track occupation condition to the pulp problem"

    S = train_sets["Paths"]
    for s in train_sets["Jtrack"].keys():
        js = train_sets["Jtrack"][s]
        for (j, jp) in itertools.combinations(js, 2):
            s_previous = previous_station(S[j], s)
            s_previousp = previous_station(S[jp], s)

            # the last condition is to keep an order if trains are folowwing one another
            if s_previous == s_previousp and s_previous != None:
                if occurs_as_pair(j, jp, train_sets["Jd"]):
                    problem += y[j][jp][s] == y[j][jp][s_previous]

            if s_previousp != None:
                LHS = delay_var[jp][s_previousp]
                LHS += earliest_dep_time(S, timetable, jp, s_previousp)
                LHS += tau(timetable, "pass", jp, s_previousp, s)
                LHS += μ*(1-y[j][jp][s])
                RHS = delay_var[j][s]
                RHS += earliest_dep_time(S, timetable, j, s)
                RHS += tau(timetable, "res")
                problem += LHS >= RHS

            if s_previous != None:
                LHS = delay_var[j][s_previous]
                LHS += earliest_dep_time(S, timetable, j, s_previous)
                LHS += tau(timetable, "pass", j, s_previous, s)
                LHS += μ*y[j][jp][s]
                RHS = delay_var[jp][s]
                RHS += earliest_dep_time(S, timetable, jp, s)
                RHS += tau(timetable, "res")
                problem += LHS >= RHS


def objective(problem, timetable, delay_var, train_sets, d_max):
    "adds objective function to the pulp problem"
    S = train_sets["Paths"]
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(timetable, i, j) /
                         d_max for i in train_sets["J"] for j in S[i] if penalty_weights(timetable, i, j) != 0])


def linear_varibles(train_sets, d_max):
    " returns all linear variables for the optimisation problem, i.e. secondary_delays_vars and order_vars"
    S = train_sets["Paths"]

    secondary_delays_vars = dict()

    for train in train_sets["J"]:
        secondary_delays_vars.update(pus.LpVariable.dicts(
            "Delays", ([train], S[train]), 0, d_max, cat='Integer'))

    order_vars = dict()

    l1 = list(train_sets["Josingle"])
    l2 = list(train_sets["Jd"])

    # this is the single and double line case
    for js in l1+l2:
        no_station = []
        for pair in itertools.combinations(js, 2):
            # common path without the last station TODO think over
            no_station = common_path(S, pair[0], pair[1])[0:-1]

            y = pus.LpVariable.dicts(
                "y", ([pair[0]], [pair[1]], no_station), 0, 1, cat='Integer')

            update_dictofdicts(order_vars, y)

    # this is the track occupation case
    for s in train_sets["Jtrack"].keys():
        for pair in itertools.combinations(train_sets["Jtrack"][s], 2):
            y = pus.LpVariable.dicts(
                "y", ([pair[0]], [pair[1]], [s]), 0, 1, cat='Integer')
            update_dictofdicts(order_vars, y)

    return secondary_delays_vars, order_vars

def create_linear_problem(train_sets, timetable, d_max, μ):
    "creates the linear problem model"
    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var, y = linear_varibles(train_sets, d_max)

    # following conditions are added
    minimal_span(prob, timetable, secondary_delays_var, y, train_sets, μ)
    minimal_stay(prob, timetable, secondary_delays_var, train_sets)
    single_line(prob, timetable, secondary_delays_var, y, train_sets, μ)
    track_occuparion(prob, timetable, secondary_delays_var, y, train_sets, μ)
    # TODO other conditions such as common resources and circ

    # objective is added
    objective(prob, timetable, secondary_delays_var, train_sets, d_max)
    return prob

def solve_linear_problem(train_sets, timetable, d_max, μ):
    "solves the linear problem returns the pulp object"
    prob = create_linear_problem(train_sets, timetable, d_max, μ)
    prob.solve()
    return prob


# auxiliary functions for visualisation

def return_delay_and_acctual_time(S, timetable, prob, j, s):
    "given the solution of the optimisation problem returns secondary delay and acctual time of leaving given station"
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            delay = v.varValue
            time = v.varValue + earliest_dep_time(S, timetable, j, s)
            return delay, time
    return 0, 0


def impact_to_objective(prob, timetable, j, s, d_max):
    "teturn the inpact to the objective of the particular secondary delay of particular train at particular station"
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            return penalty_weights(timetable, j, s)/d_max*v.varValue
    return 0.
