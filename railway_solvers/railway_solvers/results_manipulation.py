import pickle
from collections import defaultdict
from copy import deepcopy
from typing import Dict
import pandas as pd
from pulp.pulp import LpProblem
import pulp
import numpy as np


def results_to_dict(data, mode, model = None, pdict = None):
    if mode == "cqm":
        results = []
        for i in range(data['num_rows']):
            samples = data['sample_data']['data'][i]
            values = {var:val for val, var in zip(samples, data['variable_labels'])}
            results.append(values)
        return results
    elif mode == "pyqubo":
        assert pdict !=None
        assert model != None
        results = []
        for row in data.record:
            sample = {v:row[0][i] for i,v in enumerate(model.variables)}
            decoded = model.decode_sample(sample, vartype='BINARY', feed_dict=pdict)
            results.append(defaultdict(int,decoded.subh))
        return results
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
    return result, sum(x == True for x in result.values())


def is_feasible(prob, sampleset):
    return all(analyze_constraints(prob, sample)[0].values() for sample in sampleset)


def get_objective(prob, sample):
    obj = prob.objective
    result = obj.constant
    result += sum(val*sample[var.name] for var, val in obj.items())
    return result

def get_best_sample(df, sampleset,mode, prob = None, model = None, pdict = None, offset = None):
    df_feas = df[df.feas==True]
    return dict(df_feas.iloc[0])

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


def get_results(sampleset, mode, prob = None, model = None, pdict = None, offset = None):
    if mode == "cqm":
        labels = sampleset['variable_labels']
        samples = np.array(sampleset['sample_data']['data'])
        df = pd.DataFrame()
        for index, l in enumerate(labels):
            df[l] = samples[:, index]
        df["energies"] = sampleset['vectors']['energy']['data']
        df["feas"] = sampleset['vectors']['is_feasible']['data']
        df = df.sort_values('energies')
        return df
    elif mode == "pyqubo":
        assert model != None
        assert pdict != None
        assert offset != None
        assert prob != None
        samples, energies, feas = [], [], []
        for row in sampleset.record:
            sample = {v:row[0][i] for i,v in enumerate(model.variables)}
            decoded = model.decode_sample(sample, vartype='BINARY', feed_dict=pdict)
            samples.append(list(decoded.subh.values()))
            energies.append(row[1])
            feas.append(all(analyze_constraints(prob, defaultdict(int,decoded.subh))[0].values()))
        df = pd.DataFrame()
        samples = np.array(samples)
        for index, l in enumerate(prob.variables()):
            df[l] = samples[:, index]
        df['energies'] = energies
        df['feas'] = feas
        df = df.sort_values('energies')
        return df


def load_results(file_name):
    return (pickle.load(open(file_name, "rb")))