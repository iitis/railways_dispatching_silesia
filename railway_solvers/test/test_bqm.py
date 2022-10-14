import os
import logging
import importlib
import numpy as np

from railway_solvers import (annealing, create_linear_problem, convert_to_bqm)


def compute_all_files(method, pdict=None, real_anneal_var=None, sim_annealing_var=None):
    """Runs the annealing experiment for the files inside the inputs folder

    :param method: 'sim', 'real', 'hyb', 'cqm'
    :type method: str
    :param pdict: Dictionary containing penalty values
    :type pdict: Dict[str, float]
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]

    """
    for file in os.listdir("test/inputs"):
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
    file_name = f"inputs.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)
    prob = create_linear_problem(train_sets, timetable, d_max, cat = "Integer")
    sample = annealing(prob, method, pdict, real_anneal_var, sim_annealing_var)
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
    file_name = f"inputs.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)
    prob = create_linear_problem(train_sets, timetable, d_max, cat = "Integer")
    bqm, qubo, interpreter = convert_to_bqm(prob, pdict)


    vars = bqm.variables
    hs = bqm.linear
    Js = bqm.quadratic
    s = np.size(vars)

    count = 0
    ofset = 0
    for i in range(s):
        for j in range(i, s):
            if i == j:
                if hs[vars[i]] != 0:
                    count = count + 1
                    assert hs[vars[i]] == qubo[0][(vars[i], vars[i])]
                else:
                    ofset = ofset + 1
            else:
                if (vars[i], vars[j]) in Js:
                    J = Js[vars[i], vars[j]]
                    count = count + 1
                    try: 
                        assert J == qubo[0][(vars[i], vars[j])]
                    except:
                        assert J == qubo[0][(vars[j], vars[i])]

    assert count == len(qubo[0])


def test_all_files():
    #file = "5_trains_all_cases"
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
    #test_single_file(file, method, pdict=pdict)
    compute_all_files(method, pdict = pdict, sim_annealing_var=sim_annealing_var) 
