import itertools
import time
import pulp as pus


from .helpers_functions import departure_station4switches
from .helpers_functions import update_dictofdicts
from .helpers_functions import earliest_dep_time
from .helpers_functions import get_M
from .helpers_functions import tau
from .helpers_functions import not_the_same_rolling_stock
from .helpers_functions import previous_station
from .helpers_functions import occurs_as_pair
from .helpers_functions import penalty_weights
from .helpers_functions import skip_station
from .helpers_functions import previous_train_from_Jround
from .helpers_functions import subsequent_train_at_Jround
from .helpers_functions import can_MO_on_line
from .helpers_functions import are_two_trains_entering_via_the_same_switches
# variables

# order variables


def order_variables(train_sets):
    """return order variables in pus.LpVariable.dicts for constrains where
    these variables are necessary
    """
    order_vars = dict()
    order_var4single_line_constrain(order_vars, train_sets)
    order_var4minimal_span_constrain(order_vars, train_sets)
    order_var4track_occuparion_at_stations(order_vars, train_sets)
    order_var4switch_occupation(order_vars, train_sets)
    return order_vars


def order_var4single_line_constrain(order_vars, train_sets):
    """adds to nested order_vars dict order variables for single line constrains
    loop goes over all stations and suitable trains pairs

    order_var(j,jp,s,sp) = 1
    .......                            ... <-jp ..
    [s]     .                        .       [sp]
    ...........j ->..............................

    """
    for s in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][s]:
            update_y4(order_vars, j, jp, s[0], s[1])


def order_var4minimal_span_constrain(order_vars, train_sets):
    """add to nested order_vars dict  order variables for single line constrains
    loop goes over suitable stations pairs and trains pairs

     order_var(j,jp,s) = 1

     [s]
     ......j1 -> .... j -> ......

    """
    for s in train_sets["Jd"].keys():
        for all_js in train_sets["Jd"][s].values():
            for js in all_js:
                for (j, jp) in itertools.combinations(js, 2):
                    update_y3(order_vars, j, jp, s)


def order_var4track_occuparion_at_stations(order_vars, train_sets):
    """add to nested order_vars dict order variables for track occupation
    at station constrains. Loop goes over all stations and suitable trains
    pairs

    order_var(j,jp,s) = 1


        .            .
         .   [s]    .
   ..jp-> ... j -> ............
    """
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):
                update_y3(order_vars, j, jp, s)


def order_var4switch_occupation(order_vars, train_sets):
    """add to nested order_vars dict order variables for track occupation
    c - switch

    I case

    order_var(j,jp,s) = 1  (j goes first)

                 ..........
                .
    ..jp ->....c ....
       [s]   .
    ...... j


    II case

    order_var(jp, jpp, sp, spp) = 1   (jp goes first)

    [sp]
    .............jp->...
                        .   .......
                         . .  [s]
                          c........
    [spp]                .
    .jpp ->..............

    """

    for s in train_sets["Jswitch"].keys():
        for pair in train_sets["Jswitch"][s]:
            (jp, jpp) = pair.keys()

            sp = departure_station4switches(s, jp, pair, train_sets)
            spp = departure_station4switches(s, jpp, pair, train_sets)
            if sp == spp:
                if (sp != s and can_MO_on_line(jp, jpp, s, train_sets)):
                    update_y4_in(order_vars, "in", jp, jpp, s)
                else:
                    update_y3(order_vars, jp, jpp, sp)
            elif s == sp or s == spp:
                update_y4(order_vars, jp, jpp, sp, spp)
            else: # we have differen s, sp and spp
                update_y4_in(order_vars, "in", jp, jpp, s)



def update_y3(order_var, j, jp, s):
    """checks if there is an order variable for (j,jp,s) or for (jp,j,s)
    if not creates one
    """
    check1 = check_order_var_3arg(order_var, j, jp, s)
    check2 = check_order_var_3arg(order_var, jp, j, s)
    if not (check1 or check2):
        # 3 as there are 3 vars
        y = pus.LpVariable.dicts("y", ([j], [jp], ["one_station"], [s]), 0, 1, cat="Integer")
        update_dictofdicts(order_var, y)



def update_y4(order_var, j, jp, s, sp):
    """checks if there is an order variable for (j,jp,s,sp) or for (jp,j,sp,s)
    if not creates one
    """
    check1 = check_order_var_4arg(order_var, j, jp, s, sp)
    check2 = check_order_var_4arg(order_var, jp, j, sp, s)
    if not (check1 or check2):
        z = pus.LpVariable.dicts(
            "z", ([j], [jp], [s], [sp]), 0, 1, cat="Integer"
            )
        update_dictofdicts(order_var, z)


def update_y4_in(order_var, a, j, jp, s):
    """checks if there is an order variable for (a,j,jp,s) or for (a,jp,j,s)
    if not creates one
    """
    check1 = check_order_var_4arg(order_var, a, j, jp, s)
    check2 = check_order_var_4arg(order_var, a, jp, j, s)
    if not (check1 or check2):
        z = pus.LpVariable.dicts(
            "z", ([a], [j], [jp], [s]), 0, 1, cat="Integer"
            )
        update_dictofdicts(order_var, z)

def get_y3(order_var, j, jp, s):
    """gets order variable for two trains (j,jp) and one station (s)
     if there exist no such order variable, read one for reversed order (jp,j)
     and return 1-order_var

     order_var(j,jp,s) = 1

     [s]
     ......j1 -> .... j -> ......


    order_var(j,jp,s) = 0 = 1 - order_var(jp,j,s)

    [s]
    ......j -> .... j1 -> ......
    """
    if check_order_var_3arg(order_var, j, jp, s):
        return order_var[j][jp]["one_station"][s]
    else:
        return 1 - order_var[jp][j]["one_station"][s]


def get_y4_singleline(y, j, jp, s, sp):
    """gets order variable for two trains (j,jp) and two stations (s, sp), asingle track line case
     if there exist no such order variable, read one for reversed order (jp,j)
     and ans (sp,s) and return 1-order_var

    order_var(j,jp,s,sp) = 1
    .......                            ... <-jp ..
    [s]    .                          .       [sp]
    ...........j ->..............................


    order_var(j,jp,s,sp) = 0 = 1 - order_var(jp,j,sp,s)
    .......                            ...........
    [s]    .                          .       [sp]
    ...j ->...................<- jp ..............

    """
    if check_order_var_4arg(y, j, jp, s, sp):
        return y[j][jp][s][sp]
    else:
        return 1 - y[jp][j][sp][s]


def get_y4_in(y, a, j, jp, s):
    """
    as get_y4_singleline but permutes only j and jp
    """
    if check_order_var_4arg(y, a, j, jp, s):
        return y[a][j][jp][s]
    else:
        return 1 - y[a][jp][j][s]


def check_order_var_3arg(y, j, jp, s):
    """checks if in y there is an order variable for (j,jp,s) """
    return j in y and jp in y[j] and "one_station" in y[j][jp] and s in y[j][jp]["one_station"]


def check_order_var_4arg(y, j, jp, s, sp):
    """checks if in y there is an order variable for (j,jp,s,sp) """
    return j in y and jp in y[j] and s in y[j][jp] and sp in y[j][jp][s]


# delay variables


def delay_varibles(train_sets, d_max, cat):
    """returns all linear variables for the optimisation problem, i.e.
    secondary_delays_vars and order_vars
    """
    secondary_delays_vars = dict()
    for j in train_sets["J"]:
        for s in train_sets["Paths"][j]:
            if not skip_station(j,s, train_sets):
                if subsequent_train_at_Jround(train_sets, j, s) is None:

                    dvar = pus.LpVariable.dicts(
                        "Delays", ([j], [s]), 0, d_max, cat=cat
                    )

                    update_dictofdicts(secondary_delays_vars, dvar)

    return secondary_delays_vars


# encoding particular dispatching conditions


def minimal_span_constrain(
    s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max
):
    """ecnoding constrains for minimal span condition"""
    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, jp, s)

    RHS = earliest_dep_time(S, timetable, j, s)
    RHS += tau(
        timetable,
        "headway",
        first_train=j,
        second_train=jp,
        first_station=s,
        second_station=sp,
    )

    M = get_M(LHS, RHS, d_max)

    if LHS - d_max < RHS:  # otherwise always fulfilled  (redundant)
        LHS += delay_var[jp][s]
        RHS += delay_var[j][s]

        RHS -= M * get_y3(y, jp, j, s)
        problem += LHS >= RHS, f"minimal_span_{jp}_{j}_{s}_{sp}"


def minimal_span(problem, timetable, delay_var, y, train_sets, d_max):
    """adds the minimum span condition to the pulp problem

    [s1] ..... j1 -> ....... j2 -> ..... [s2]
                      span
    """

    for s in train_sets["Jd"].keys():
        for sp in train_sets["Jd"][s].keys():
            for js in train_sets["Jd"][s][sp]:
                for (j, jp) in itertools.combinations(js, 2):

                    minimal_span_constrain(
                        s,
                        sp,
                        j,
                        jp,
                        problem,
                        timetable,
                        delay_var,
                        y,
                        train_sets,
                        d_max,
                    )
                    minimal_span_constrain(
                        s,
                        sp,
                        jp,
                        j,
                        problem,
                        timetable,
                        delay_var,
                        y,
                        train_sets,
                        d_max,
                    )


def single_line_constrain(
    s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max
):
    """encoding constrsains for the single line condition """
    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, j, s)
    RHS = earliest_dep_time(S, timetable, jp, sp)
    RHS += tau(timetable, "pass", first_train=jp, first_station=sp, second_station=s)

    M = get_M(LHS, RHS, d_max)

    if LHS - d_max < RHS:  # otherwise always fulfilled (redundant)
        LHS += delay_var[j][s]

        RHS += delay_var[jp][sp]
        RHS -= M * get_y4_singleline(y, j, jp, s, sp)

        problem += LHS >= RHS, f"single_line_{j}_{jp}_{s}_{sp}"


def single_line(problem, timetable, delay_var, y, train_sets, d_max):
    """adds single line condition to the pulp problem

    .......                            ... <-j2 ..
    [s1]   .                          .       [s2]
    ..j1 ->.......................................

    """

    for (s, sp) in train_sets["Josingle"].keys():
        for (j, jp) in train_sets["Josingle"][(s, sp)]:
            if not_the_same_rolling_stock(j, jp, train_sets):

                single_line_constrain(
                    s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max
                )
                single_line_constrain(
                    sp, s, jp, j, problem, timetable, delay_var, y, train_sets, d_max
                )


def minimal_stay_constrin(j, s, problem, timetable, delay_var, train_sets):
    """encoding constrsains for minimal stay condition """
    S = train_sets["Paths"]

    sp = previous_station(S[j], s)
    if sp is not None:
        if s in delay_var[j]: #all provided delay var exists:

            LHS = delay_var[j][s]
            LHS += earliest_dep_time(S, timetable, j, s)

            RHS = delay_var[j][sp]
            RHS += earliest_dep_time(S, timetable, j, sp)
            RHS += tau(
                timetable, "pass", first_train=j, first_station=sp, second_station=s
            )
            RHS += tau(timetable, "stop", first_train=j, first_station=s)

            problem += (LHS >= RHS, f"minimal_stay_{j}_{s}")
            # schedule is ensured by delay_var[j][s] >= 0


def minimal_stay(problem, timetable, delay_var, train_sets):
    """adds minimal stay on the staiton to the pulp problem """

    for j in train_sets["J"]:
        for s in train_sets["Paths"][j]:
            minimal_stay_constrin(
                j, s, problem, timetable, delay_var, train_sets
            )


# station -- track occupation


def keep_trains_order(
    s, j, jp, problem, y, train_sets
):
    """Helper for single track occupation at the station constrain

    if two trains follow each other s′ -> s, i.e. j,j′∈ Jd and (s′,s)∈ Cjj′
     we requires y(j,j′,s′) = y(j,j′,s)

     .................
                       .
                        .   [s]
     ....j1 -> ...j2 ->..............
     [s']
     """
    S = train_sets["Paths"]
    sp = previous_station(S[j], s)
    if sp in train_sets["Jd"].keys():
        if s in train_sets["Jd"][sp].keys():
            # if both trains goes sp -> s and have common path
            if occurs_as_pair(j, jp, train_sets["Jtrack"][s]):
                if not can_MO_on_line(j, jp, s, train_sets):
                    # the order on station y[j][jp][s] must be the same as
                    # on the path y[j][jp][sp] (previous station)
                    if s in y[j][jp]["one_station"] and sp in y[j][jp]["one_station"]:
                        problem += (
                            y[j][jp]["one_station"][s] == y[j][jp]["one_station"][sp],
                            f"track_occupation_{j}_{jp}_{s}_{sp}",
                        )
                elif are_two_trains_entering_via_the_same_switches(train_sets, s, j, jp):
                    problem += (
                                get_y4_in(y, "in", j, jp, s) == y[j][jp]["one_station"][s],
                                f"track_occupation_{j}_{jp}_{s}_{sp}",
                                )


def trains_order_at_s(
    s, j, jp, problem, timetable, delay_var, y, train_sets, d_max
):
    """helper for track occupation condition """

    S = train_sets["Paths"]

    j_rr = subsequent_train_at_Jround(train_sets, j, s)
    if j_rr is not None: # train under investigation terminates at s and goes
    #to the subseguent train that uses the same rolling stock
        problem +=  (
                get_y3(y, jp, j, s) == get_y3(y, jp, j_rr, s),
                f"track_occupation_{j}_{jp}_{j_rr}_{s}",
                )
    else: #train goes further, if incuded in track occupation it has to go further

        j_r = previous_train_from_Jround(train_sets, jp, s)
        sp = previous_station(S[jp], s)

        if j_r is not None: #first station, but train tied with j_r
            s_rp = previous_station(S[j_r], s)

            LHS = earliest_dep_time(S, timetable, j_r, s_rp)
            LHS += tau(
                    timetable, "pass", first_train=j_r, first_station=s_rp, second_station=s
                    )

        elif sp is not None: # previous station in the route of j

            LHS = earliest_dep_time(S, timetable, jp, sp)
            LHS += tau(
                timetable, "pass", first_train=jp, first_station=sp, second_station=s
            )

        else: # this means first station
            LHS = earliest_dep_time(S, timetable, jp, s)

        RHS = earliest_dep_time(S, timetable, j, s)

        if "add_swithes_at_s" in train_sets.keys():
            if (
                s in train_sets["add_swithes_at_s"]
            ):  # this is the approximation used in  ArXiv:2107.03234,
                RHS += tau(timetable, "res")

        M = get_M(LHS, RHS, d_max)

        if LHS - d_max < RHS:

            if j_r is not None: #first station, but train tied with j_r
                LHS += delay_var[j_r][s_rp]

            elif sp is not None: #previous station existis
                LHS += delay_var[jp][sp]

            RHS -= M * get_y3(y, jp, j, s)
            LHS -= delay_var[j][s]

            problem += LHS >= RHS, f"track_occupation_{j}_{jp}_{s}_p"




def track_occuparion(problem, timetable, delay_var, y, train_sets, d_max):
    """adds track occupation condition to the pulp problem
    ..j1 ->.....
                .   [s]
    ..j2 ->..............

    """

    S = train_sets["Paths"]
    for s in train_sets["Jtrack"].keys():
        for js in train_sets["Jtrack"][s]:
            for (j, jp) in itertools.combinations(js, 2):

                if not_the_same_rolling_stock(j, jp, train_sets):
                    skip = "skip_station" in train_sets and jp in train_sets["skip_station"] and s in train_sets["skip_station"][jp]
                    if not skip:
                        keep_trains_order(
                            s,
                            j,
                            jp,
                            problem,
                            y,
                            train_sets,
                        )
                    
                        trains_order_at_s(
                            s,
                            jp,
                            j,
                            problem,
                            timetable,
                            delay_var,
                            y,
                            train_sets,
                            d_max,
                        )

                    skip = "skip_station" in train_sets and j in train_sets["skip_station"] and s in train_sets["skip_station"][j]
                    if not skip:
                        trains_order_at_s(
                            s,
                            j,
                            jp,
                            problem,
                            timetable,
                            delay_var,
                            y,
                            train_sets,
                            d_max,
                        )


#switch occupation condition at stations


def switch_occ(
    s, jp, sp, jpp, spp, problem, timetable, delay_var, y, train_sets, d_max
):

    S = train_sets["Paths"]

    LHS = earliest_dep_time(S, timetable, jp, sp)
    RHS = earliest_dep_time(S, timetable, jpp, spp)

    RHS += tau(
        timetable, "res", first_train=jp, second_train=jpp, first_station=s
        )
    if s != sp:
        LHS += tau(
            timetable, "pass", first_train=jp, first_station=sp, second_station=s
        )

    if s != spp:
        RHS += tau(
            timetable, "pass", first_train=jpp, first_station=spp, second_station=s
        )

    M = get_M(LHS, RHS, d_max)

    if LHS < RHS + d_max:

        if spp == sp:
            if sp != s and can_MO_on_line(jp, jpp, s, train_sets):
                RHS -= M * get_y4_in(y, "in", jp, jpp, s)
            else:
                RHS -= M * get_y3(y, jp, jpp, sp)
        elif s == spp or s == sp:
            RHS -= M * get_y4_singleline(y, jp, jpp, sp, spp)
        else: # s, sp and spp differs
            RHS -= M * get_y4_in(y, "in", jp, jpp, s)

        LHS += delay_var[jp][sp]
        RHS += delay_var[jpp][spp]

        problem += LHS >= RHS, f"switch_{jp}_{jpp}_{s}_{sp}_{spp}"



def switch_occupation(problem, timetable, delay_var, y, train_sets, d_max):
    """adds switch occupation condition to the pulp problem

    j1 -> --------------
    [s1]                .
    j2 -> -------------- c ----
                          .  [s2]
                           .......

    """

    for s in train_sets["Jswitch"].keys():
        for pair in train_sets["Jswitch"][s]:
            (jp, jpp) = pair.keys()
            if not_the_same_rolling_stock(jp, jpp, train_sets):

                sp = departure_station4switches(s, jp, pair, train_sets)
                spp = departure_station4switches(s, jpp, pair, train_sets)

                switch_occ(
                    s,
                    jp,
                    sp,
                    jpp,
                    spp,
                    problem,
                    timetable,
                    delay_var,
                    y,
                    train_sets,
                    d_max,
                )
                switch_occ(
                    s,
                    jpp,
                    spp,
                    jp,
                    sp,
                    problem,
                    timetable,
                    delay_var,
                    y,
                    train_sets,
                    d_max,
                )


def rolling_stock_circ(problem, timetable, delay_var, train_sets, d_max):
    """adds rolling stock circulation condition to the pulp problem"""
    S = train_sets["Paths"]

    for s in train_sets["Jround"].keys():
        for (j, jp) in train_sets["Jround"][s]:

            sp = previous_station(S[j], s)
            LHS = earliest_dep_time(S, timetable, j, sp)
            RHS = earliest_dep_time(S, timetable, jp, s)
            LHS += tau(
                timetable, "pass", first_train=j, first_station=sp, second_station=s
            )
            LHS += tau(timetable, "prep", first_train=jp, first_station=s)

            if RHS < LHS + d_max:
                LHS += delay_var[j][sp]
                RHS += delay_var[jp][s]

                problem += RHS >= LHS, f"circulation_{j}_{jp}_{s}"


def objective(problem, timetable, delay_var, train_sets, d_max):
    """adds objective function to the pulp problem"""
    S = train_sets["Paths"]
    problem += pus.lpSum(
        [
            delay_var[i][j] * penalty_weights(timetable, i, j) / d_max
            for i in train_sets["J"]
            for j in S[i]
            if penalty_weights(timetable, i, j) != 0
        ]
    )


def create_linear_problem(train_sets, timetable, d_max, cat):
    """creates the linear problem model"""
    prob = pus.LpProblem("Trains", pus.LpMinimize)

    secondary_delays_var = delay_varibles(train_sets, d_max, cat = cat)
    y = order_variables(train_sets)

    # following conditions are added
    minimal_span(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    minimal_stay(prob, timetable, secondary_delays_var, train_sets)
    single_line(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    track_occuparion(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    rolling_stock_circ(prob, timetable, secondary_delays_var, train_sets, d_max)
    switch_occupation(prob, timetable, secondary_delays_var, y, train_sets, d_max)

    # objective is added
    objective(prob, timetable, secondary_delays_var, train_sets, d_max)

    return prob


def solve_linear_problem(train_sets, timetable, d_max, cat = "Integer"):
    """solves the linear problem returns the pulp object"""
    prob = create_linear_problem(train_sets, timetable, d_max, cat)
    start_time = time.time()
    prob.solve()
    print("optimisation, time = ", time.time() - start_time, "seconds")

    return prob


# auxiliary functions for visualisation


def delay_and_acctual_time(train_sets, timetable, prob, j, s):
    """given the solution of the optimisation problem returns secondary delay
    and actual time of leaving given station
    """
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            delay = v.varValue
            time = v.varValue + earliest_dep_time(train_sets["Paths"], timetable, j, s)
            return delay, time


def impact_to_objective(prob, timetable, j, s, d_max):
    """return the impact to the objective of the particular secondary delay
    of particular train at particular station
    """
    for v in prob.variables():
        if v.name == f"Delays_{j}_{s}":
            return penalty_weights(timetable, j, s) / d_max * v.varValue
    return 0.0
