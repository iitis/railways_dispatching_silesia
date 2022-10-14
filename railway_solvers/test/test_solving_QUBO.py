import os
import logging
import importlib
import numpy as np

from railway_solvers import (create_linear_problem, annealing, 
                             convert_to_bqm, count_quadratic_couplings, 
                             get_results, count_linear_fields, get_best_feasible_sample,
                             store_result, load_results)


def compute_all_files(method, pdict=None, real_anneal_var=None, sim_annealing_var=None):
    """Runs the annealing experiment for the files inside the inputs folder

    :param method: 'sim', 'real', 'hyb', 'cqm'
    :type method: str
    :param pdict: Dictionary containing penalty values
    :type pdict: Dict[str, float]
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]

    """
    for file in os.listdir("test/inputs4QUBO"):
        if "init" not in file and "pycach" not in file and ".pytest_cache" not in file:
            compute_single_file(file[:-3], method, pdict, real_anneal_var, sim_annealing_var)


def compute_single_file(
    file, method,  pdict=None, real_anneal_var=None, sim_annealing_var=None
):
    """Runs the annealing experiment for the files inside the inputs folder

    :param file: Name of the input data file
    :type file: str
    :param method: 'sim', 'real', 'hyb', 'cqm'
    :type method: str
    :param pdict: Dictionary containing penalty values
    :type pdict: Dict[str, float]
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]
    """
    print(file)
    file_name = f"inputs4QUBO.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)
    prob = create_linear_problem(train_sets, timetable, d_max, cat = "Integer")
    bqm, _, interpreter = convert_to_bqm(prob, pdict)
    sampleset = annealing(bqm, interpreter, method, pdict, real_anneal_var, sim_annealing_var)
    dict_list = get_results(sampleset, prob=prob)
    store_result(f"test/annealing_results/{file_name}", sampleset)
    load_results(f"test/annealing_results/{file_name}")
    sample = get_best_feasible_sample(dict_list)
    assert sample["feasible"] == True



def test_qubo():
    file = "5_trains_all_cases"
    pdict = {
        "minimal_span": 2.5,
        "single_line": 2.5,
        "minimal_stay": 2.5,
        "track_occupation": 2.5,
        "switch": 2.5,
        "occupation": 2.5,
        "circulation": 2.5,
        "objective": 1,
    }
    file_name = f"inputs4QUBO.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)
    prob = create_linear_problem(train_sets, timetable, d_max, cat = "Integer")
    bqm, qubo, interpreter = convert_to_bqm(prob, pdict)


    vars = bqm.variables
    hs = bqm.linear
    Js = bqm.quadratic
    s = np.size(vars)

    count = 0
    for i in range(s):
        for j in range(i, s):
            if i == j:
                if hs[vars[i]] != 0:
                    count = count + 1
                    assert hs[vars[i]] == qubo[0][(vars[i], vars[i])]
            else:
                if (vars[i], vars[j]) in Js:
                    J = Js[vars[i], vars[j]]
                    count = count + 1
                    try: 
                        assert J == qubo[0][(vars[i], vars[j])]
                    except:
                        assert J == qubo[0][(vars[j], vars[i])]

    assert count == len(qubo[0])

    assert len(bqm.linear) == count_linear_fields(bqm)

    assert len(bqm.quadratic) == count_quadratic_couplings(bqm)


def test_all_files():
    #real_anneal_var = {"num_reads": 1000, "annealing_time": 20, "chain_strength": 4}
    sim_annealing_var = {"beta_range": (0.001, 10), "num_sweeps": 100, "num_reads": 100}
    method = "sim"
    pdict = {
        "minimal_span": 2.5,
        "single_line": 2.5,
        "minimal_stay": 2.5,
        "track_occupation": 2.5,
        "switch": 2.5,
        "occupation": 2.5,
        "circulation": 2.5,
        "objective": 1,
    }
    compute_all_files(method, pdict = pdict, sim_annealing_var=sim_annealing_var) 
