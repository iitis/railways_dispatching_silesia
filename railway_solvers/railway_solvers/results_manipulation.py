import pickle
from typing import Dict

import dimod
from pulp.pulp import LpProblem
import pulp


def analyze_constraints(prob: LpProblem, sample: Dict):
    result = {}
    for cname, c in prob.constraints.items():
        sense = c.sense
        expr = sum(val * sample[var.name] for var, val in c.items())
        if sense == pulp.LpConstraintEQ:
            result[cname] = expr == -c.constant
        elif sense == pulp.LpConstraintLE:
            result[cname] = expr <= -c.constant
        elif sense == pulp.LpConstraintGE:
            result[cname] = expr >= -c.constant
    return result, sum(x == True for x in result.values())


def get_objective(prob, sample):
    obj = prob.objective
    result = obj.constant
    result += sum(val * sample[var.name] for var, val in obj.items())
    return result


def get_best_fesible_sample(dict_list):
    for l in dict_list:
        if l['feasible']:
            return l


def pyqubo_sample_to_dict(sample, interpreter = None, prob = None):
    decoded = interpreter(sample)
    decoded_dict  = {**decoded.subh, **decoded.sample}
    return {v: decoded_dict[v] for v in map(str,prob.variables())}


def get_results(sampleset, mode, prob = None, interpreter = None):
    dict_list = []
    for data in sampleset.data():
        if mode == "cqm":
            sample = interpreter(data.sample)
        elif mode == "pyqubo":
            sample = pyqubo_sample_to_dict(data.sample, interpreter = interpreter, prob= prob)
        rdict = {}
        rdict['energy'] = data.energy
        rdict['objective'] = round(get_objective(prob, sample), 2)
        rdict['feasible'] = all(analyze_constraints(prob, sample)[0].values())
        rdict['sample'] = sample
        rdict['feas_constraints'] = analyze_constraints(prob, sample)
        dict_list.append(rdict)
    return sorted(dict_list, key=lambda d: d['objective'])


def store_result(file_name, sampleset):
    sdf = sampleset.to_serializable()
    with open(file_name, 'wb') as handle:
        pickle.dump(sdf, handle)


def load_results(file_name):
    file = pickle.load(open(file_name, "rb"))
    return  dimod.SampleSet.from_serializable(file)
