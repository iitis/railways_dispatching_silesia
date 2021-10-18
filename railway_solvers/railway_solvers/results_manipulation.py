from copy import deepcopy
from typing import Dict

from pulp.pulp import LpProblem
import pulp

def results_to_dict(data, mode):
    if mode == "cqm":
        results = []
        for i in range(data['num_rows']):
            samples = data['sample_data']['data'][i]
            values = {var:val for val, var in zip(samples, data['variable_labels'])}
            results.append(values)
        return results
    elif mode == "pyqubo":
        pass
    else:
        raise "unrecognized mode"
    pass

def analyze_constraints(prob:LpProblem, sample: Dict):
    result = {}
    for cname, c in prob.constraints.items():
        sense = c.sense
        expr = sum(val*sample[var.name] for var, val in c.items())
        if sense == pulp.LpConstraintEQ:
            result[cname] = expr == -c.constant
        elif sense == pulp.LpConstraintLE:
            result[cname] = expr <= -c.constant
        elif sense == pulp.LpConstraintGE:
            result[cname] = expr >= -c.constant
    return result

def is_feasible(prob, sample):
    return all(analyze_constraints(prob, sample).values())

def get_objective(prob, sample):
    obj = prob.objective
    result = obj.constant
    result += sum(val*sample[var.name] for var, val in obj.items())
    return result