import itertools

import pulp as pus

from .helpers_functions import *


def minimal_span(problem, timetable, delay_var, y, train_sets, d_max, μ):
    "adds the minimum span condition to the pulp problem"

    S = train_sets["Paths"]
    for s in train_sets["Jd"].keys():
        for sp in train_sets["Jd"][s].keys():
            for js in train_sets["Jd"][s][sp]:
                for (j, jp) in itertools.combinations(js, 2):


                    LHS = earliest_dep_time(S, timetable, jp, s)
                    LHS -= earliest_dep_time(S, timetable, j, s)
                    RHS = tau(timetable, 'blocks', first_train=j, second_train = jp, first_station=s, second_station=sp)

                    # otherwise almost fulfilled TODO will be further tested
                    if LHS - d_max < RHS:

                        #LHS - d_max - smallest possible LHS
                        LHS += delay_var[jp][s]
                        LHS += μ*(1-y[j][jp][s])
                        LHS -= delay_var[j][s]
                        problem += LHS >= RHS, f"minimal_span_{jp}_{j}_{s}_{sp}"


                    LHS = earliest_dep_time(S, timetable, j, s)
                    LHS -= earliest_dep_time(S, timetable, jp, s)
                    RHS = tau(timetable, 'blocks', first_train=jp, second_train = j, first_station=s, second_station=sp)
                    # otherwise almost fulfilled
                    if LHS - d_max < RHS:

                        LHS += delay_var[j][s]
                        LHS += μ*y[j][jp][s]
                        LHS -= delay_var[jp][s]
                        problem += LHS >= RHS, f"minimal_span_{j}_{jp}_{s}_{sp}"



def rolling_stock_circ(problem, timetable, delay_var, train_sets, d_max):
    " adds rolling stock circulation condition to the pulp problem"
    S = train_sets["Paths"]

    for s in train_sets["Jround"].keys():
        for (j, jp) in train_sets["Jround"][s]:

            sp = previous_station(S[j], s)
            LHS = earliest_dep_time(S, timetable, j, sp)
            RHS = earliest_dep_time(S, timetable, jp, s)
            LHS += tau(timetable, 'pass', first_train=j, first_station=sp, second_station=s)
            LHS += tau(timetable, 'prep', first_train=jp, first_station=s)

            if RHS < LHS + d_max:
                LHS += delay_var[j][sp]
                RHS += delay_var[jp][s]

                problem += RHS >= LHS, f"circulation_{j}_{jp}_{s}"


def switch_occuparion(problem, timetable, delay_var, y, train_sets, d_max, μ):
    " adds switch occupation condition to the pulp problem"
    S = train_sets["Paths"]

    for s in train_sets["Jswitch"].keys():
        for (sp, spp, jp, jpp) in train_sets["Jswitch"][s]:

            LHS = earliest_dep_time(S, timetable, jp, sp)
            RHS = earliest_dep_time(S, timetable, jpp, spp)
            RHS  += tau(timetable, 'res', first_train=jp, second_train=jpp, first_station=s)
            if s != sp:
                LHS += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)

            if s != spp:
                RHS += tau(timetable, 'pass', first_train=jpp, first_station=spp, second_station=s)

            if LHS < RHS + d_max:
                if sp == spp:
                    try:
                        LHS += μ*(y[jp][jpp][sp])
                    except:
                        LHS += μ*(1-y[jpp][jp][sp])
                else:
                    try:
                        LHS += μ*(y[jp][jpp][sp][spp])
                    except:
                        LHS += μ*(1-y[jpp][jp][spp][sp])

                LHS += delay_var[jp][sp]
                RHS += delay_var[jpp][spp]

                problem += LHS >= RHS, f"switch_{jp}_{jpp}_{s}_{sp}_{spp}"


            LHS = earliest_dep_time(S, timetable, jpp, spp)
            RHS = earliest_dep_time(S, timetable, jp, sp)
            RHS  += tau(timetable, 'res', first_train=jpp, second_train=jp, first_station=s)
            if s != spp:
                LHS += tau(timetable, 'pass', first_train=jpp, first_station=spp, second_station=s)

            if s != sp:
                RHS += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)

            if LHS < RHS + d_max:

                if sp == spp:
                    try:
                        LHS += μ*(1-y[jp][jpp][sp])
                    except:
                        LHS += μ*(y[jpp][jp][sp])
                else:
                    try:
                        LHS += μ*(1-y[jp][jpp][sp][spp])
                    except:
                        LHS += μ*(1-y[jpp][jp][spp][sp])


                LHS += delay_var[jpp][spp]
                RHS += delay_var[jp][sp]

                problem += LHS >= RHS, f"switch_{jpp}_{jp}_{s}_{spp}_{sp}"



def single_line(problem, timetable, delay_var, y, train_sets, d_max, μ):
    " adds single line condition to the pulp problem"
    S = train_sets["Paths"]

    for (s, sp) in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][(s, sp)]:



            LHS = earliest_dep_time(S, timetable, j, s)
            RHS = earliest_dep_time(S, timetable, jp, sp)
            RHS += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)
            #RHS += tau(timetable, 'res', first_train=jp, second_train=j, first_station=s)


            # otherwise almost fulfilled
            if LHS - d_max < RHS:

                LHS += delay_var[j][s]
                LHS += μ*(y[j][jp][s][sp])
                LHS -= delay_var[jp][sp]

                problem += LHS >= RHS, f"single_line_{j}_{jp}_{s}_{sp}"


            LHS = earliest_dep_time(S, timetable, jp, sp)
            RHS = earliest_dep_time(S, timetable, j, s)
            RHS += tau(timetable, 'pass', first_train=j, first_station=s, second_station=sp)
            #RHS += tau(timetable, 'res', first_train=j, second_train=jp, first_station=s)

            if LHS - d_max < RHS:

                LHS += delay_var[jp][sp]
                LHS += μ*(1-y[j][jp][s][sp])
                LHS -= delay_var[j][s]

                problem += LHS >= RHS, f"single_line_{jp}_{j}_{s}_{sp}"

    #print(problem)

def minimal_stay(problem, timetable, delay_var, train_sets):
    "adds minimum stay condition to the pulp problem"
    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]

    for j in train_sets["J"]:
        for s in S[j]:
            sp = previous_station(S[j], s)
            if (sp != None and s != not_considered_station[j]):
                problem += delay_var[j][s] >= delay_var[j][sp], f"minimal_stay_{j}_{s}"


def track_occuparion(problem, timetable, delay_var, y, train_sets, d_max, μ):
    "adds track occupation condition to the pulp problem"

    S = train_sets["Paths"]
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):
                sp = previous_station(S[j], s)
                spp = previous_station(S[jp], s)

                # the last condition is to keep an order if trains are folowing one another
                if sp == spp and sp != None:
                    if sp in train_sets["Jd"].keys():
                        if s in train_sets["Jd"][sp].keys():
                            if occurs_as_pair(j, jp, train_sets["Jd"][sp][s]):
                                problem += y[j][jp][s] == y[j][jp][sp], f"track_occupation_{j}_{jp}_{s}_{sp}"


                if spp != None:

                    LHS = earliest_dep_time(S, timetable, jp, spp)
                    LHS += tau(timetable, "pass", first_train=jp, first_station=spp, second_station=s)
                    RHS = earliest_dep_time(S, timetable, j, s)
                    RHS += tau(timetable, "res")

                    if LHS - d_max < RHS:
                        LHS += μ*(1-y[j][jp][s])
                        LHS -= delay_var[j][s]
                        LHS += delay_var[jp][spp]

                        problem += LHS >= RHS, f"track_occupation_{j}_{jp}_{s}_p"

                if sp != None:

                    LHS = earliest_dep_time(S, timetable, j, sp)
                    LHS += tau(timetable, "pass", first_train=j, first_station=sp, second_station=s)
                    RHS = earliest_dep_time(S, timetable, jp, s)
                    RHS += tau(timetable, "res")

                    if LHS - d_max < RHS:
                        LHS = delay_var[j][sp]
                        LHS += μ*y[j][jp][s]
                        RHS += delay_var[jp][s]

                        problem += LHS >= RHS, f"track_occupation_{j}_{jp}_{s}"


def objective(problem, timetable, delay_var, train_sets, d_max):
    "adds objective function to the pulp problem"
    S = train_sets["Paths"]
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(timetable, i, j) /
                         d_max for i in train_sets["J"] for j in S[i] if penalty_weights(timetable, i, j) != 0])


def linear_varibles(train_sets, d_max):
    " returns all linear variables for the optimisation problem, i.e. secondary_delays_vars and order_vars"
    S = train_sets["Paths"]

    secondary_delays_vars = dict()

    for j in train_sets["J"]:
        secondary_delays_vars.update(pus.LpVariable.dicts(
            "Delays", ([j], S[j]), 0, d_max, cat='Integer'))

    order_vars = dict()

    # order variables for single line trains going in opposite direction
    for s in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][s]:

            y = pus.LpVariable.dicts("y", ([j], [jp], [s[0]], [s[1]]), 0, 1, cat='Integer')
            update_dictofdicts(order_vars, y)

    # order variables for trains sequence
    for s in train_sets["Jd"].keys():
        for all_js in train_sets["Jd"][s].values():
            for js in all_js:
                for (j, jp) in itertools.combinations(js, 2):

                    y = pus.LpVariable.dicts(
                        "y", ([j], [jp], [s]), 0, 1, cat='Integer')

                    update_dictofdicts(order_vars, y)


    # this is the track occupation case
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):
                y = pus.LpVariable.dicts(
                    "y", ([j], [jp], [s]), 0, 1, cat='Integer')
                update_dictofdicts(order_vars, y)

    # switch occupacy

    for s in train_sets["Jswitch"].keys():
        for (sp, spp, jp, jpp) in train_sets["Jswitch"][s]:
            if sp == spp:
                try:
                    order_vars[jp][jpp][sp]
                except:
                    try:
                        order_vars[jp][jpp][sp]
                    except:
                        y = pus.LpVariable.dicts(
                            "y", ([jp], [jpp], [sp]), 0, 1, cat='Integer')
                        update_dictofdicts(order_vars, y)
            else:
                try:
                    order_vars[jp][jpp][sp][spp]
                except:
                    try:
                        order_vars[jp][jpp][sp][spp]
                    except:
                        y = pus.LpVariable.dicts(
                            "y", ([jp], [jpp], [sp], [spp]), 0, 1, cat='Integer')
                        update_dictofdicts(order_vars, y)

    return secondary_delays_vars, order_vars

def create_linear_problem(train_sets, timetable, d_max, μ):
    "creates the linear problem model"
    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var, y = linear_varibles(train_sets, d_max)

    # following conditions are added
    minimal_span(prob, timetable, secondary_delays_var, y, train_sets, d_max, μ)
    minimal_stay(prob, timetable, secondary_delays_var, train_sets)
    single_line(prob, timetable, secondary_delays_var, y, train_sets, d_max, μ)
    track_occuparion(prob, timetable, secondary_delays_var, y, train_sets, d_max, μ)
    rolling_stock_circ(prob, timetable, secondary_delays_var, train_sets, d_max)
    switch_occuparion(prob, timetable, secondary_delays_var, y, train_sets, d_max, μ)

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
    "given the solution of the optimisation problem returns secondary delay and actual time of leaving given station"
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            delay = v.varValue
            time = v.varValue + earliest_dep_time(S, timetable, j, s)
            return delay, time
    return 0, 0


def impact_to_objective(prob, timetable, j, s, d_max):
    "return the impact to the objective of the particular secondary delay of particular train at particular station"
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            return penalty_weights(timetable, j, s)/d_max*v.varValue
    return 0.
