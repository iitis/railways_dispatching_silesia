"""analyze constraints, objective etc. of the solution"""
import pickle
from typing import Any, Dict, List, Tuple
import dimod
import pulp
from pulp.pulp import LpProblem

def analyze_constraints(
    prob: LpProblem, sample: Dict[str, int]
) -> Tuple[Dict[str, bool], int]:
    """check which constraints were satisfied

    :param prob: analyzed integer model
    :type prob: LpProblem
    :param sample: samples generated by the optimizer
    :type sample: Dict[str,int]
    :return: dictionary mapping constraint to whether they were satisfied, and
    the number of satisfied constraints
    :rtype: Dict[str,bool]
    """
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
    return result, sum(x is True for x in result.values())

def get_objective(prob: pulp.LpProblem, sample) -> float:
    """computes objective value for sample

    :param prob: the integer program with the relevant objective function
    :type prob: pulp.LpProblem
    :param sample: analyzed sample
    :type sample: [type]
    :return: value of the objective funtion
    :rtype: float
    """
    obj = prob.objective
    result = obj.constant
    result += sum(val * sample[var.name] for var, val in obj.items())
    return result

def get_best_feasible_sample(dict_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """output first feasible sample in the list

    :param dict_list: list of analyzed samples
    :type dict_list: List[Dict[str,Any]]
    :return: first feasible sample
    :rtype: Dict[str,Any]
    """
    best_feasible =  next((l for l in dict_list if l["feasible"]), None)
    if best_feasible:
        return best_feasible
    return sorted(dict_list, key=lambda d: d["energy"])[0]

def get_results(
    sampleset: dimod.SampleSet, prob: pulp.LpProblem
) -> List[Dict[str, Any]]:
    """Check samples one by one, and computes it statistics.

    Statistics includes energy (as provided by D'Wave), objective function
    value, feasibility analysis, the samples itself. Samples are sorted
    according to value of the objetive function

    :param sampleset: analyzed samples
    :type sampleset: dimod.SampleSet
    :param prob: integer problem according to which samples are analyzed
    :type prob: pulp.LpProblem
    :return: analyzed samples, sorted according to objective
    :rtype: List[Dict[str,Any]]
    """
    dict_list = []
    for data in sampleset.data():
        rdict = {}
        sample = data.sample
        rdict["energy"] = data.energy
        rdict["objective"] = round(get_objective(prob, sample), 2)
        rdict["feasible"] = all(analyze_constraints(prob, sample)[0].values())
        rdict["sample"] = sample
        rdict["feas_constraints"] = analyze_constraints(prob, sample)
        dict_list.append(rdict)
    return sorted(dict_list, key=lambda d: d["objective"])

def save_results(
    file_name: str, sampleset: dimod.SampleSet, 
) -> List[Dict[str, Any]]:
    """
    :param sampleset: analyzed samples
    :type sampleset: dimod.SampleSet
    :return: analyzed samples, sorted according to objective
    :rtype: List[Dict[str,Any]]
    """
    dict_list = []
    for data in sampleset.data():
        rdict = {}
        rdict["sample"] = data.sample
        rdict["energy"] = data.energy
        dict_list.append(rdict)
    with open(file_name, "wb") as handle:
        pickle.dump(dict_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

def read_process_results(
    file, prob: pulp.LpProblem
) -> List[Dict[str, Any]]:
    """
    Read sample from file.
    Format list of dict fileds:
    - sample
    - energy
    Check samples one by one, and computes it statistics.

    Statistics includes energy (as provided by D'Wave), objective function
    value, feasibility analysis, the samples itself. Samples are sorted
    according to value of the objetive function


    :param prob: integer problem according to which samples are analyzed
    :type prob: pulp.LpProblem
    :return: analyzed samples, sorted according to objective
    :rtype: List[Dict[str,Any]]
    """
    with open(file, 'rb') as handle:
        samples = pickle.load(handle)
    dict_list = []
    for data in samples:
        rdict = {}
        sample = data["sample"]
        #print(sample)
        rdict["energy"] = data["energy"]
        rdict["objective"] = round(get_objective(prob, sample), 2)
        rdict["feasible"] = all(analyze_constraints(prob, sample)[0].values())
        rdict["sample"] = sample
        rdict["feas_constraints"] = analyze_constraints(prob, sample)
        dict_list.append(rdict)
    return sorted(dict_list, key=lambda d: d["objective"])

def print_results(dict_list):
    """pront some fetures of solution """
    soln = next((l for l in dict_list if l["feasible"]), None)
    if soln is not None:
        print("obj:", soln["objective"], "x:", list(soln["sample"].values()))
        print("First 10 solutions")
        for d in dict_list[:10]:
            print(d)
    else:
        print("No feasible solution")
        for d in dict_list[:10]:
            print(
                "Energy:",
                d["energy"],
                "Objective:",
                d["objective"],
                "Feasible",
                d["feasible"],
                "Broken constraints:",
                d["feas_constraints"][1],
            )


##### QUBO provessing
def count_quadratic_couplings(bqm):
    """
    returns number of copulings - Js
    """
    count = 0
    for J in bqm.quadratic.values():
        if J != 0:
            count = count + 1
    return count


def count_linear_fields(bqm):
    """
    return number of local fields hs
    """ 
    count = 0
    for h in bqm.linear.values():
        if h != 0:
            count = count + 1
    return count     
