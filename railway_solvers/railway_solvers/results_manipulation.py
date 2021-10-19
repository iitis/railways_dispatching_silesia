import pickle
from typing import Dict
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
        if l['feasible'] == True:
            return l


def sample_to_dict(sample, mode, var_names=None, model=None, pdict=None):
    if mode == "cqm":
        return {var: val for val, var in zip(sample, var_names)}
    elif mode == "pyqubo":
        sample_dict = {v: sample[0][i] for i, v in enumerate(model.variables)}
        decoded = model.decode_sample(sample_dict, vartype='BINARY', feed_dict=pdict)
        vars = decoded.subh
        for v in model.variables:
            if v not in decoded.subh:
                vars[v] = decoded.sample[v]
        return vars
    else:
        raise "unrecognized mode"
    pass


def get_results(sampleset, mode, prob=None, model=None, pdict=None, offset=None):
    dict_list = []
    sample_size = sampleset['num_rows'] if mode == "cqm" else len(sampleset.record)
    for i in range(sample_size):
        rdict = {}
        if mode == "cqm":
            varlist = sampleset['variable_labels']
            sample = sample_to_dict(sampleset['sample_data']['data'][i], mode, var_names=varlist)
            rdict['energy'] = sampleset['vectors']['energy']['data'][i]
        elif mode == "pyqubo":
            assert model != None
            assert pdict != None
            assert prob != None
            sample = sample_to_dict(sampleset.record[i], mode, model=model, pdict=pdict)
            rdict['energy'] = sampleset.record[i][1]
        else:
            raise "unrecognized mode"
        rdict['objective'] = round(get_objective(prob, sample), 2)
        rdict['feasible'] = all(analyze_constraints(prob, sample)[0].values())
        rdict['sample'] = sample
        rdict['feas_constraints'] = analyze_constraints(prob, sample)
        dict_list.append(rdict)
    result = sorted(dict_list, key=lambda d: d['objective'])
    return result


def store_result(file_name, sampleset, mode):
    if mode == "cqm":
        sdf = sampleset.to_serializable()
        with open(file_name, 'wb') as handle:
            pickle.dump(sdf, handle)
    elif mode == "pyqubo":
        with open(file_name, 'wb') as handle:
            pickle.dump(sampleset, handle)
    else:
        raise "unrecognized mode"


def load_results(file_name):
    return (pickle.load(open(file_name, "rb")))
