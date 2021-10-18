from dimod.constrained import cqm_to_bqm
import pulp
import dimod
from railway_solvers import convert_to_cqm


def _compare_bqm(bqm1, bqm2):
    outcome = True
    quadratic1, linear1, offset1 = bqm1.to_ising()
    quadratic2, linear2, offset2 = bqm2.to_ising()
    outcome &= sorted(quadratic1.values()) == sorted(quadratic2.values())
    outcome &= sorted(linear1.values()) == sorted(linear2.values())
    outcome &= offset1 == offset2
    return outcome


def test_equality_binary():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], cat="Binary"))
    # print([v.cat for v in vars.values()])
    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) == 1
    pulp_problem += sum((i+1)*vars[i] for i in range(n))
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Binary(f"y_{i}") for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) == 1, label="_C1")
    cqm.set_objective(sum((i+1)*var_dwave[i] for i in range(n)))

    assert cqm_to_bqm(dwave_pulp_problem)[0] == cqm_to_bqm(cqm)[0]

def test_equality():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) == 1
    pulp_problem += sum((i+1)*vars[i] for i in range(n))
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) == 1, label="_C1")
    cqm.set_objective(sum((i+1)*var_dwave[i] for i in range(n)))

    assert cqm_to_bqm(dwave_pulp_problem)[0] == cqm_to_bqm(cqm)[0]

def test_geq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) >= 3
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) >= 3, label="_C1")
    cqm.set_objective(var_dwave[0]-var_dwave[0])

    bqm1 = cqm_to_bqm(dwave_pulp_problem, lagrange_multiplier=1)[0]
    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(bqm1, bqm2)

def test_leq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) <= 1
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) <= 1, label="_C1")


    bqm1 = cqm_to_bqm(dwave_pulp_problem, lagrange_multiplier=1)[0]
    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(bqm1, bqm2)

def test_leq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 5, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) <= 17
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=15) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) +15 <= 17, label="_C1")


    bqm1 = cqm_to_bqm(dwave_pulp_problem, lagrange_multiplier=1)[0]
    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(bqm1, bqm2)

def test_bad_leq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))
    print(vars)

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) <= 1
    dwave_pulp_problem = convert_to_cqm(pulp_problem)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) <= 2, label="_C1")

    bqm1 = cqm_to_bqm(dwave_pulp_problem, lagrange_multiplier=1)[0]
    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert not _compare_bqm(bqm1, bqm2)



