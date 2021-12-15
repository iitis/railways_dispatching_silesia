from copy import deepcopy
from typing import Callable, Tuple

import dimod
import pulp
from dimod import ConstrainedQuadraticModel
from dimod.constrained import ConstrainedQuadraticModel
from dimod.sampleset import SampleSet
from pulp import LpProblem


def _is_binary(var: pulp.LpVariable) -> bool:
    """Checks if var is a bit. This means that it is an Integer, with bounds 0
and 1

    :param var: checked variable
    :type var: pulp.LpVariable
    :return: flag if variable is bit
    :rtype: bool
    """
    result = var.cat == pulp.LpInteger
    result = result and var.lowBound == 0
    return result and var.upBound == 1


def convert_to_cqm(model: LpProblem) -> Tuple[ConstrainedQuadraticModel, Callable]:
    """Converts Integer program into ConstrainedQuadraticModel. As second object
outputs function interpreting the results. Works only if all variables are
bounded integers.

    :param model: model to be converted
    :type model: LpProblem
    :return: the same integer model for dimod, and function interpreting the results
    :rtype: Tuple[ConstrainedQuadraticModel, Callable]
    """
    cqm = ConstrainedQuadraticModel()

    # vars translator
    vars_trans = dict()
    for var in model.variables():
        if _is_binary(var):
            vars_trans[var] = dimod.Binary(var.name)
        elif var.cat == pulp.LpInteger:
            lb = var.lowBound
            ub = var.upBound
            vars_trans[var] = dimod.Integer(
                var.name, lower_bound=0, upper_bound=ub-lb)+lb
        else:
            assert var.cat != pulp.LpContinuous

    # constraints
    for cname, c in model.constraints.items():
        sense = c.sense
        expr = sum(val*vars_trans[var] for var, val in c.items())
        if sense == pulp.LpConstraintEQ:
            new_c = expr == -c.constant
        elif sense == pulp.LpConstraintLE:
            new_c = expr <= -c.constant
        elif sense == pulp.LpConstraintGE:
            new_c = expr >= -c.constant
        cqm.add_constraint(new_c, label=cname)

    # objective
    if model.objective:
        assert model.sense == pulp.LpMinimize, "Converter works only for minimization problems"

        obj = model.objective
        dimod_obj = 0
        dimod_obj += obj.constant
        dimod_obj += sum(val*vars_trans[var] for var, val in obj.items())
        cqm.set_objective(dimod_obj)

    def interpreter(sampleset, model):
        result = []
        energies = [d.energy for d in sampleset.data()]
        for sample in sampleset.samples():
            new_sample = {}
            for name in sampleset.variables:
                var = next(i for i in model.variables() if i.name==name)
                new_sample[name] = var.lowBound + sample[name]
            result.append(new_sample)
        return dimod.SampleSet.from_samples(dimod.as_samples(result), 'BINARY', energies)

    return cqm, lambda ss: interpreter(ss, model)
