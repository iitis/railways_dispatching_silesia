import os
import importlib
import numpy as np

from railway_solvers import (
    create_linear_problem,
    annealing,
    convert_to_bqm,
    count_quadratic_couplings,
    get_results,
    count_linear_fields,
    get_best_feasible_sample,
    save_results,
    read_process_results,
    print_results
    )

train_sets = None
timetable = None
d_max = None

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
    our_samples, info = annealing(bqm, interpreter, method, real_anneal_var, sim_annealing_var) 
    assert info['beta_range'] == (0.001, 10)

    save_results(f"test/annealing_results/{file_name}", our_samples)
    dict_list1 = read_process_results(f"test/annealing_results/{file_name}", prob)
    dict_list = get_results(our_samples, prob=prob)
    assert dict_list == dict_list1
    print_results(dict_list)
    sample = get_best_feasible_sample(dict_list1)
    assert sample["feasible"] is True
    assert len(sample["feas_constraints"][0]) == sample["feas_constraints"][1]
    assert all(sample["feas_constraints"][0].values())

    if file_name == "inputs4QUBO.two_trains_going_one_way_simplest":
        assert sample["objective"] == 0.2
    elif file_name == "inputs4QUBO.rolling_stock_circulation":
        assert sample["objective"] == 0.4
    elif file_name == "inputs4QUBO.mo_on_the_line":
        assert sample["objective"] < 1.2


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
    bqm, qubo, _ = convert_to_bqm(prob, pdict)

    variables = bqm.variables
    hs = bqm.linear
    Js = bqm.quadratic
    s = np.size(variables)
    count = 0
    for i in range(s):
        for j in range(i, s):
            if i == j:
                if hs[variables[i]] != 0:
                    count = count + 1
                    assert hs[variables[i]] == qubo[0][(variables[i], variables[i])]
            else:
                if (variables[i], variables[j]) in Js:
                    J = Js[variables[i], variables[j]]
                    count = count + 1
                    try: 
                        assert J == qubo[0][(variables[i], variables[j])]
                    except:
                        assert J == qubo[0][(variables[j], variables[i])]
    assert count == len(qubo[0])
    assert len(bqm.linear) == count_linear_fields(bqm)
    assert len(bqm.quadratic) == count_quadratic_couplings(bqm)

def test_all_files():
    """test simple examples on simulated annealing. It is probabilistic test"""
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
