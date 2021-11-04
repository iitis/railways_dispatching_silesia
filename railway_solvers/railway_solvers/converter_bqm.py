import pulp
import dimod
from pulp import LpProblem
from pulp.constants import LpMinimize
from .converter_cqm import _is_binary
from pyqubo import Binary, LogEncInteger, Placeholder
import re

def _get_placeholder(cname):
    if re.match("minimal_span_", cname):
        return Placeholder("minimal_span")
    if re.match("circulation_", cname):
        return Placeholder("circulation")
    if re.match("single_line_", cname):
        return Placeholder("single_line")
    if re.match("minimal_stay_", cname):
        return Placeholder("minimal_stay")
    if re.match("track_occupation_", cname):
        return Placeholder("track_occupation")
    raise ValueError(f"{cname} not handled")


# for LE
def _get_slack_ub(data, offset):
    ub = sum(val*(var.upBound if val<0 else var.lowBound) for var, val in data)
    result = -(ub + offset)
    assert int(result) == result
    return int(result)


def convert_to_pyqubo(model: LpProblem):
    H = 0

    # vars translator
    vars_trans = dict()
    for var in model.variables():
        assert var.cat != pulp.LpContinuous
        if _is_binary(var):
            vars_trans[var] = Binary(var.name)
        else:
            lb = var.lowBound
            ub = var.upBound
            vars_trans[var] = LogEncInteger(var.name, (lb, ub))

    # constraints
    for cname, c in model.constraints.items():
        sense = c.sense
        expr = sum(val*vars_trans[var] for var, val in c.items())
        expr += c.constant

        values = [val for _, val in c.items()]
        ph = _get_placeholder(cname)
        if sense == pulp.LpConstraintEQ:
            H += ph * expr**2
        elif sense == pulp.LpConstraintLE:
            slack = LogEncInteger(cname, (0, _get_slack_ub(c.items(), c.constant)))
            H += ph * (expr+slack)**2
        elif sense == pulp.LpConstraintGE:
            slack = LogEncInteger(cname, (0, _get_slack_ub([(var,-val) for var, val in c.items()], -c.constant)))
            H += ph * (expr-slack)**2

    # # objective
    if model.objective:
        assert model.sense == LpMinimize
        obj = model.objective
        pyqubo_obj = 0
        pyqubo_obj += obj.constant
        pyqubo_obj += sum(val*vars_trans[var] for var, val in obj.items())
        H += Placeholder("objective") * pyqubo_obj
    return H.compile()


def convert_to_bqm(model: LpProblem, pdict):
    pyqubo_model = convert_to_pyqubo(model)

    def interpreter(sampleset):
        result = []
        energies = [d.energy for d in sampleset.data()]
        for sample in sampleset.samples():
            decoded = (pyqubo_model.decode_sample(dict(sample), vartype='BINARY', feed_dict=pdict))
            decoded_dict = {**decoded.subh, **decoded.sample}
            result.append({v: decoded_dict[v] for v in map(str, model.variables())})
        return dimod.SampleSet.from_samples(dimod.as_samples(result), 'BINARY', energies)

    return pyqubo_model.to_bqm(feed_dict=pdict), lambda ss: interpreter(ss)
