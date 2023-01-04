import re
from typing import Callable, Dict, List, Tuple

import dimod
import pulp
import pyqubo
from pulp import LpProblem
from pulp.constants import LpMinimize
from pyqubo import Binary, LogEncInteger, Placeholder

from .converter_cqm import _is_binary


def _get_placeholder(cname: str) -> Placeholder:
    """Output placeholder (penalty constant) of the name appropriate to the
    constraint name. Typically Placeholder is chosen based on the beginning of the
    name of the constraint name.

        :param cname: name of the constraint
        :type cname: str
        :raises ValueError: if the constraint name does not match any known placeholder
        :return: appropriate placeholder
        :rtype: Placeholder
    """
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
    if re.match("switch_", cname):
        return Placeholder("switch")
    if re.match("circulation_", cname):
        return Placeholder("circulation")
    raise ValueError(f"{cname} not handled")


def _get_slack_ub(data: List[int], offset: int) -> int:
    """Generate the lowerbound of the slack variable xi, which appears when
    transforming a*x <= b with a*x + xi <= b. slack variable is nonnegative. all
    arguments should be integers.

        :param data: List of integers a for a*x <= b
        :type data: List[int]
        :param offset: offset b for a*x <= b
        :type offset: int
        :return: lowerbound of the slack variable
        :rtype: int
    """
    ub = sum(val * (var.upBound if val < 0 else var.lowBound) for var, val in data)
    result = -(ub + offset)
    assert int(result) == result
    return int(result)


def convert_to_pyqubo(model: LpProblem) -> pyqubo.Model:
    """Converts Integer program into pyqubo.Model. Placeholders (penalty
    parameters) are NOT set up. Names of placeholders can be found in the code of
    _get_placeholder function, and for objective there is extra Placeholder called "objective".

        :param model: model to be converted
        :type model: LpProblem
        :return: the same compiled integer model for pyqubo
        :rtype: pyqubo.Model
    """
    H = 0

    # vars translator
    vars_trans = {}
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
        expr = sum(val * vars_trans[var] for var, val in c.items())
        expr += c.constant

        ph = _get_placeholder(cname)
        if sense == pulp.LpConstraintEQ:
            H += ph * expr ** 2
        elif sense == pulp.LpConstraintLE:
            slack = LogEncInteger(cname, (0, _get_slack_ub(c.items(), c.constant)))
            H += ph * (expr + slack) ** 2
        elif sense == pulp.LpConstraintGE:
            slack = LogEncInteger(
                cname,
                (
                    0,
                    _get_slack_ub([(var, -val) for var, val in c.items()], -c.constant),
                ),
            )
            H += ph * (expr - slack) ** 2

    # # objective
    if model.objective:
        assert model.sense == LpMinimize
        obj = model.objective
        pyqubo_obj = 0
        pyqubo_obj += obj.constant
        pyqubo_obj += sum(val * vars_trans[var] for var, val in obj.items())
        H += Placeholder("objective") * pyqubo_obj
    return H.compile()


def convert_to_bqm(
    model: LpProblem, pdict: Dict[str, float]
) -> Tuple[dimod.BinaryQuadraticModel, Callable]:
    """Converts Integer program into pyqubo.Model. Placeholders (penalty
    parameters) are set up based on pdict. Names of placeholders can be found in the code of
    _get_placeholder function, and for objective there is extra Placeholder called "objective".

        :param model: model to be converted
        :type model: LpProblem
        :param pdict: dictionary with penalty values
        :type pdict: Dict[str,float]
        :return: the same integer model for dimod, and function interpreting the results
        :rtype: Tuple[dimod.BinaryQuadraticModel,Callable]
    """
    pyqubo_model = convert_to_pyqubo(model)

    def interpreter(sampleset):
        result = []
        energies = [d.energy for d in sampleset.data()]
        for sample in sampleset.samples():
            decoded = pyqubo_model.decode_sample(
                dict(sample), vartype="BINARY", feed_dict=pdict
            )
            decoded_dict = {**decoded.subh, **decoded.sample}
            result.append({v: decoded_dict[v] for v in map(str, model.variables())})
        return dimod.SampleSet.from_samples(
            dimod.as_samples(result), "BINARY", energies
        )

    return pyqubo_model.to_bqm(feed_dict=pdict), pyqubo_model.to_qubo(feed_dict=pdict), lambda ss: interpreter(ss)
