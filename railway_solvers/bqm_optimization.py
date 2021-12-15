from Qfile_solve import *
from railway_solvers import convert_to_bqm, store_result, get_results, load_results, get_best_feasible_sample, \
    create_linear_problem, convert_to_cqm, solve_linear_problem
import os
import logging
import importlib


def get_file_name(input_name, method, train_route, num_reads=None, annealing_time=None, chain_strength=None):
    folder = f"annealing_results\{input_name}"
    if not os.path.exists(folder):
        os.mkdir(folder)
    fname = f"{method}_{train_route}"
    if num_reads != None:
        fname += f"_{num_reads}_{annealing_time}_{chain_strength}"
    return os.path.join(folder, fname)


def log_experiment(folder, file_name, bqm, dict_list):
    logging.basicConfig(filename=os.path.join(f"annealing_results\{folder}", 'results.log'), level=logging.INFO)
    logging.info("------------------------new run---------------------")
    logging.info(file_name)
    logging.info(f"Number of variables: {len(bqm.variables)}")
    logging.info(f"Best Sample, {get_best_feasible_sample(dict_list)}")
    logging.info("Samples:")
    for d in dict_list[:50]:
        logging.info(d)


def get_parameters(real_anneal_var_dict):
    if real_anneal_var_dict == None:
        num_reads = 1000
        annealing_time = 250
        chain_strength = 4
    else:
        num_reads = real_anneal_var_dict['num_reads']
        annealing_time = real_anneal_var_dict['annealing_time']
        chain_strength = real_anneal_var_dict['chain_strength']

    return num_reads, annealing_time, chain_strength


def annealing(prob, method, train_route, input_name, pdict=None, real_anneal_var_dict=None):
    """ Inputs:==
        prob: The problem,
        method: 'sim', 'real',
        train_route: 'default' , 'rerouted'
        pdict: Dictionary of penalties
        real_anneal_var_dict: dictionary containing 'num_reads', 'annealing_time' and 'chain_strength' i.e. real annealing variables
        Returns:==  Dict of feasible solution
    """
    assert method in ["sim", "real", "hyb", "cqm"]
    file_name = get_file_name(input_name, method, train_route)
    if method == "cqm":
        cqm, interpreter = convert_to_cqm(prob)
        sampleset = constrained_solver(cqm)
    else:
        bqm, interpreter = convert_to_bqm(prob, pdict)
        if method == 'sim':
            sampleset = sim_anneal(bqm, num_sweeps=1000, num_reads=1000)
        elif method == 'real':
            num_reads, annealing_time, chain_strength = get_parameters(real_anneal_var_dict)
            file_name = get_file_name(input_name, method, train_route, num_reads, annealing_time, chain_strength)
            sampleset = real_anneal(bqm, num_reads=num_reads, annealing_time=annealing_time, chain_strength=chain_strength)
        elif method == 'hyb':
            sampleset = hybrid_anneal(bqm)

    store_result(file_name, sampleset)
    sampleset = interpreter(load_results(file_name))
    dict_list = get_results(sampleset, prob=prob)
    log_experiment(input_name, file_name, bqm, dict_list)


def test_all_files(method, train_route = "default", pdict=None, real_anneal_var=None):
    for file in os.listdir("inputs"):
        if "init" not in file and "pycach" not in file:
            test_single_file(file[:-3], method, train_route, pdict, real_anneal_var)


def test_single_file(file, method, train_route = "default", pdict=None, real_anneal_var=None):
    file_name = f"inputs.{file}"
    mdl = importlib.import_module(file_name)
    globals().update(mdl.__dict__)
    if train_route == 'default':
        prob = create_linear_problem(train_sets, timetable, d_max)
    elif train_route == "rerouted":
        prob = create_linear_problem(train_sets_rerouted, timetable, d_max)
    annealing(prob, method, train_route, file_name, pdict)


if __name__ == "__main__":
    file = "linear_solver"
    file = "5_trains_all_cases"
    real_anneal_var = {"num_reads": 1000, "annealing_time": 20, "chain_strength": 4}
    method = 'sim'
    pdict = {"minimal_span": 2.5, "single_line": 2.5, "minimal_stay": 2.5, "track_occupation": 2.5, "switch": 2.5,
             "occupation": 2.5, "circulation": 2.5, "objective": 1}
    test_single_file(file, method, pdict = pdict)
    #test_all_files(method, pdict = pdict) logging not working properly
