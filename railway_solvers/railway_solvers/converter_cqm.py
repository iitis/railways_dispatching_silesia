from copy import deepcopy
from dimod.sampleset import SampleSet
import pulp
import dimod
from pulp import LpProblem


def _is_binary(var):
    result = var.cat == pulp.LpInteger
    result = result and var.lowBound == 0
    return result and var.upBound == 1


def convert_to_cqm(model: LpProblem):
    cqm = dimod.ConstrainedQuadraticModel()

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
        result = deepcopy(sampleset)
        for i in range(result['num_rows']):
            for j, name in enumerate(result['variable_labels']):
                var = next(i for i in model.variables() if i.name==name)
                result['sample_data']['data'][i][j] += var.lowBound
        return result

    def interpreter2(sample, model):
        for key in sample:
            var = next(i for i in model.variables() if i.name==key)
            sample[key] += var.lowBound
        return sample

    return cqm, lambda ss: interpreter2(ss, model)