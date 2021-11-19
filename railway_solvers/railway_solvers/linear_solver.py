import itertools
import pulp as pus
import time
from .helpers_functions import *



def get_y_j_jp_s(y, j, jp, s):
    try:
        return y[jp][j][s]
    except:
        return 1-y[j][jp][s]

def get_y_j_jp_s_sp(y, j, jp, s, sp):
    try:
        return y[j][jp][s][sp]
    except:
        return 1-y[jp][j][sp][s]

def minimal_s(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ):
    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, jp, s)
    LHS -= earliest_dep_time(S, timetable, j, s)
    RHS = tau(timetable, 'blocks', first_train=j, second_train = jp, first_station=s, second_station=sp)

    #LHS - d_max - smallest possible LHS -- otherwise always fulfilled
    if LHS - d_max < RHS:

        LHS += delay_var[jp][s]
        LHS += μ*get_y_j_jp_s(y, j, jp, s)
        LHS -= delay_var[j][s]
        problem += LHS >= RHS, f"minimal_span_{jp}_{j}_{s}_{sp}"


def minimal_span(problem, timetable, delay_var, y, train_sets, d_max, μ):
    "adds the minimum span condition to the pulp problem"

    " ..... j1 -> ....... j2 -> ....."
    "              span              "

    S = train_sets["Paths"]
    for s in train_sets["Jd"].keys():
        for sp in train_sets["Jd"][s].keys():
            for js in train_sets["Jd"][s][sp]:
                for (j, jp) in itertools.combinations(js, 2):

                    minimal_s(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ)
                    minimal_s(s, sp, jp, j, problem, timetable, delay_var, y, train_sets, d_max, μ)



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



def switch_occ(s, sp, spp, jp, jpp, problem, timetable, delay_var, y, train_sets, d_max, μ):

    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, jp, sp)
    RHS = earliest_dep_time(S, timetable, jpp, spp)
    RHS  += tau(timetable, 'res', first_train=jp, second_train=jpp, first_station=s)
    if s != sp:
        LHS += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)

    if s != spp:
        RHS += tau(timetable, 'pass', first_train=jpp, first_station=spp, second_station=s)

    if LHS < RHS + d_max:
        if sp == spp:
            LHS += μ*get_y_j_jp_s(y, jp, jpp, sp)

        else:
            LHS += μ*get_y_j_jp_s_sp(y, jp, jpp, sp, spp)


        LHS += delay_var[jp][sp]
        RHS += delay_var[jpp][spp]

        problem += LHS >= RHS, f"switch_{jp}_{jpp}_{s}_{sp}_{spp}"



def switch_occuparion(problem, timetable, delay_var, y, train_sets, d_max, μ):
    " adds switch occupation condition to the pulp problem"

    "  ------         "
    "         \       "
    "---------  c ----"

    S = train_sets["Paths"]

    for s in train_sets["Jswitch"].keys():
        for (sp, spp, jp, jpp) in train_sets["Jswitch"][s]:
            if not_the_same_rolling_stock(jp, jpp, train_sets):

                switch_occ(s, sp, spp, jp, jpp, problem, timetable, delay_var, y, train_sets, d_max, μ)
                switch_occ(s, spp, sp, jpp, jp, problem, timetable, delay_var, y, train_sets, d_max, μ)



def single_l(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ):
    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, j, s)
    RHS = earliest_dep_time(S, timetable, jp, sp)
    RHS += tau(timetable, 'pass', first_train=jp, first_station=sp, second_station=s)

    # otherwise almost fulfilled
    if LHS - d_max < RHS:

        LHS += delay_var[j][s]
        LHS += μ*get_y_j_jp_s_sp(y, j, jp, s, sp)

        LHS -= delay_var[jp][sp]
        problem += LHS >= RHS, f"single_line_{j}_{jp}_{s}_{sp}"


def single_line(problem, timetable, delay_var, y, train_sets, d_max, μ):
    " adds single line condition to the pulp problem"

    " ......                            ......  "
    "       \                          /        "
    " .j1 ->............................. <-j2.."


    for (s, sp) in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][(s, sp)]:
            if not_the_same_rolling_stock(j, jp, train_sets):

                single_l(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ)
                single_l(sp, s, jp, j, problem, timetable, delay_var, y, train_sets, d_max, μ)


def minimal_stay(problem, timetable, delay_var, train_sets):
    "adds minimum stay condition to the pulp problem"
    not_considered_station = train_sets["skip_station"]

    S = train_sets["Paths"]

    for j in train_sets["J"]:
        for s in S[j]:
            sp = previous_station(S[j], s)
            if (sp != None and s != not_considered_station[j]):
                problem += delay_var[j][s] >= delay_var[j][sp], f"minimal_stay_{j}_{s}"

def trains_order_if_follows(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ):
    if sp in train_sets["Jd"].keys():
        if s in train_sets["Jd"][sp].keys():
            #if trains have common path
            if occurs_as_pair(j, jp, train_sets["Jd"][sp][s]):
                problem += y[j][jp][s] == y[j][jp][sp], f"track_occupation_{j}_{jp}_{s}_{sp}"

def trains_order_at_s(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ):

    if sp != None:
        S = train_sets["Paths"]

        LHS = earliest_dep_time(S, timetable, jp, sp)
        LHS += tau(timetable, "pass", first_train=jp, first_station=sp, second_station=s)
        RHS = earliest_dep_time(S, timetable, j, s)
        RHS += tau(timetable, "res")

        if LHS - d_max < RHS:
            LHS += μ*get_y_j_jp_s(y, j, jp, s)
            LHS -= delay_var[j][s]
            LHS += delay_var[jp][sp]

            problem += LHS >= RHS, f"track_occupation_{j}_{jp}_{s}_p"


def track_occuparion(problem, timetable, delay_var, y, train_sets, d_max, μ):
    "adds track occupation condition to the pulp problem"

    S = train_sets["Paths"]
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):
                sp = previous_station(S[j], s)
                spp = previous_station(S[jp], s)

                if not_the_same_rolling_stock(j, jp, train_sets):

                    trains_order_if_follows(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ)
                    trains_order_at_s(s, spp, j, jp, problem, timetable, delay_var, y, train_sets, d_max, μ)
                    trains_order_at_s(s, sp, jp, j, problem, timetable, delay_var, y, train_sets, d_max, μ)



def objective(problem, timetable, delay_var, train_sets, d_max):
    "adds objective function to the pulp problem"
    S = train_sets["Paths"]
    problem += pus.lpSum([delay_var[i][j] * penalty_weights(timetable, i, j) /
                         d_max for i in train_sets["J"] for j in S[i] if penalty_weights(timetable, i, j) != 0])



def update_y_j_jp_s(order_vars, j, jp, s):
    try:
        order_vars[j][jp][s]
    except:
        try:
            order_vars[jp][j][s]
        except:
            y = pus.LpVariable.dicts(
                "y", ([j], [jp], [s]), 0, 1, cat='Integer')

            update_dictofdicts(order_vars, y)


def update_y_j_jp_s_ps(order_vars, j, jp, s, sp):
    try:
        order_vars[j][jp][s][sp]
    except:
        try:
            order_vars[jp][j][sp][s]
        except:
            y = pus.LpVariable.dicts(
                "y", ([j], [jp], [s], [sp]), 0, 1, cat='Integer')

            update_dictofdicts(order_vars, y)


def order_variables(train_sets, d_max):
    S = train_sets["Paths"]

    order_vars = dict()

    # order variables for single line trains going in opposite direction
    for s in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][s]:
            update_y_j_jp_s_ps(order_vars, j, jp, s[0], s[1])


    # order variables for trains sequence
    for s in train_sets["Jd"].keys():
        for all_js in train_sets["Jd"][s].values():
            for js in all_js:
                for (j, jp) in itertools.combinations(js, 2):
                    update_y_j_jp_s(order_vars, j, jp, s)


    # this is the track occupation case
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):
                update_y_j_jp_s(order_vars, j, jp, s)


    # switch occupacy
    for s in train_sets["Jswitch"].keys():
        for (sp, spp, jp, jpp) in train_sets["Jswitch"][s]:
            # if jp and jpp starts from the same station
            if sp == spp:
                update_y_j_jp_s(order_vars, jp, jpp, sp)
            else:
                update_y_j_jp_s_ps(order_vars, jp, jpp, sp, spp)


    return order_vars


def delay_varibles(train_sets, d_max):
    " returns all linear variables for the optimisation problem, i.e. secondary_delays_vars and order_vars"
    S = train_sets["Paths"]

    secondary_delays_vars = dict()

    for j in train_sets["J"]:
        secondary_delays_vars.update(pus.LpVariable.dicts(
            "Delays", ([j], S[j]), 0, d_max, cat='Integer'))

    return secondary_delays_vars



def create_linear_problem(train_sets, timetable, d_max, μ):
    "creates the linear problem model"
    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var = delay_varibles(train_sets, d_max)
    y = order_variables(train_sets, d_max)

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
    start_time = time.time()
    prob.solve()
    print("optimisation, time = ", time.time() - start_time, "seconds")

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
