from dimod.constrained import _LowerBounds, cqm_to_bqm
import pulp
import dimod
from railway_solvers import convert_to_bqm
import pytest

def _compare_bqm(bqm1, bqm2):
    outcome = True
    linear1, quadratic1, offset1 = bqm1.to_ising()
    linear2, quadratic2, offset2 = bqm2.to_ising()
    outcome &= sorted(quadratic1.values()) == sorted(quadratic2.values())
    outcome &= sorted(linear1.values()) == sorted(linear2.values())
    outcome &= offset1 == offset2
    return outcome

def test_equality_binary():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], cat="Binary"))
    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) == 1, "minimal_span_1"
    pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, 
            "single_line" : 1,
            "minimal_stay" : 1,
            "track_occupation" : 1,
            "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Binary(f"y_{i}") for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) == 1, label="_C1")
    cqm.set_objective(sum((i+1)*var_dwave[i] for i in range(n)))

    assert dwave_pulp_problem == cqm_to_bqm(cqm, 1)[0]

def test_equality():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 7, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) == 1, "minimal_span_1"
    pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=7) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) == 1, label="_C1")
    cqm.set_objective(sum((i+1)*var_dwave[i] for i in range(n)))

    bqm1 = cqm_to_bqm(cqm, 1)[0]
    assert _compare_bqm(dwave_pulp_problem, bqm1)

def test_geq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 3, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) >= 1, "minimal_span_1"
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=3) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(-sum(var_dwave) <= -1)
    # cqm.set_objective(var_dwave[0]-var_dwave[0])

    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(dwave_pulp_problem, bqm2)

@pytest.mark.skip(reason="test won't work, unless lb!=0 implemented")
def test_geq_negative():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], -10, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(val*var for var, val in zip(vars.values(),[-1,2,3])) >= 3, "minimal_span_1"
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Integer(f"y_{i}", lower_bound=-10, upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) >= 3, label="_C1")
    cqm.set_objective(var_dwave[0]-var_dwave[0])

    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(dwave_pulp_problem, bqm2)

def test_leq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) <= 1, "minimal_span_1"
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) <= 1, label="_C1")

    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert _compare_bqm(dwave_pulp_problem, bqm2)

# @pytest.mark.skip(reason="implement bqm_to_cqm first")
def test_bad_leq():
    n = 3

    vars = dict()
    for i in range(n):
        vars.update(pulp.LpVariable.dicts("y", [i], 0, 20, cat="Integer"))

    pulp_problem = pulp.LpProblem("simple_test")
    pulp_problem += sum(vars.values()) <= 1, "minimal_span_1"
    # pulp_problem += sum((i+1)*vars[i] for i in range(n))
    pdict = {"minimal_span" : 1, "objective" : 1}
    dwave_pulp_problem = convert_to_bqm(pulp_problem, pdict)

    var_dwave = [dimod.Integer(f"y_{i}", upper_bound=20) for i in range(n)]
    cqm = dimod.ConstrainedQuadraticModel()
    cqm.add_constraint(sum(var_dwave) <= 2, label="_C1")

    bqm2 = cqm_to_bqm(cqm, lagrange_multiplier=1)[0]
    assert not _compare_bqm(dwave_pulp_problem, bqm2)



