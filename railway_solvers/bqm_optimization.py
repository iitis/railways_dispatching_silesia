from typing import Tuple

from Qfile_solve import *
from railway_solvers import (
    convert_to_bqm,
    store_result,
    get_results,
    load_results,
    get_best_feasible_sample,
    create_linear_problem,
    convert_to_cqm,
)
import os
import logging
import importlib


def get_file_name(
    input_name,
    method,
    num_reads=None,
    annealing_time=None,
    chain_strength=None,
) -> str:
    """Generates a file name based on the given parameters

    :param input_name: Name of the input data
    :type input_name: str
    :param method: method of execution
    :type method: str
    :param num_reads: Number of reads in QA
    :type num_reads: int
    :param annealing_time: Annealing time for QA
    :type annealing_time: int
    :param chain_strength: Chain strength for QA
    :type chain_strength: int
    :return: name of the file to be stored
    :rtype: str
    """
    folder = f"annealing_results/{input_name}"
    if not os.path.exists(folder):
        os.mkdir(folder)
    fname = f"{method}"
    if num_reads != None:
        fname += f"_{num_reads}_{annealing_time}_{chain_strength}"
    return os.path.join(folder, fname)


def log_experiment(folder, file_name, bqm, dict_list):
    """Creates a log file for the experiment to monitor experiment results

    :param folder: Name of the folder to store the log file
    :type folder: str
    :param file_name: Name of the log file
    :type file_name: str
    :param bqm: Binary quadratic model used in the experiment
    :type bqm: BinaryQuadraticModel
    :param dict_list: Analyzed samples sorted according to objective
    :type dict_list: List[Dict[str,Any]]
    """

    logging.basicConfig(
        filename=os.path.join(f"annealing_results/{folder}", "results.log"),
        level=logging.INFO,
    )
    logging.info("------------------------new run---------------------")
    logging.info(file_name)
    logging.info(f"Number of variables: {len(bqm.variables)}")
    logging.info(f"Best Sample, {get_best_feasible_sample(dict_list)}")
    logging.info("Samples:")
    for d in dict_list[:50]:
        logging.info(d)


def get_parameters(real_anneal_var_dict) -> Tuple[int, int, int]:
    """Extracts/sets parameters for annealing experiment

    :param real_anneal_var_dict: Parameters for QA experiment
    :type real_anneal_var_dict: Dict[str, float]
    :return: Number of reads, annealing_time and chain strength
    :rtype: Tuple[int, int, int]
    """
    if real_anneal_var_dict == None:
        num_reads = 1000
        annealing_time = 250
        chain_strength = 4
    else:
        num_reads = real_anneal_var_dict["num_reads"]
        annealing_time = real_anneal_var_dict["annealing_time"]
        chain_strength = real_anneal_var_dict["chain_strength"]

    return num_reads, annealing_time, chain_strength


def annealing(
    prob, method, input_name, pdict=None, real_anneal_var_dict=None
):
    """Performs the annealing experiment

    :param prob: The problem instance
    :type prob: pulp.pulp.LpProblem
    :param method: 'sim', 'real', 'hyb', 'cqm'
    :type method: str
    :param input_name: name of the input data
    :type input_name: str
    :param pdict: Dictionary containing penalty values
    :type pdict: Dict[str, float]
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]
    """

    assert method in ["sim", "real", "hyb", "cqm"]
    file_name = get_file_name(input_name, method)
    if method == "cqm":
        cqm, interpreter = convert_to_cqm(prob)
        sampleset = constrained_solver(cqm)
    else:
        bqm, interpreter = convert_to_bqm(prob, pdict)
        if method == "sim":
            sampleset = sim_anneal(bqm, num_sweeps=1000, num_reads=1000)
        elif method == "real":
            num_reads, annealing_time, chain_strength = get_parameters(
                real_anneal_var_dict
            )
            file_name = get_file_name(
                input_name,
                method,
                num_reads,
                annealing_time,
                chain_strength,
            )
            sampleset = real_anneal(
                bqm,
                num_reads=num_reads,
                annealing_time=annealing_time,
                chain_strength=chain_strength,
            )
        elif method == "hyb":
            sampleset = hybrid_anneal(bqm)

    store_result(file_name, sampleset)
    sampleset = interpreter(load_results(file_name))
    dict_list = get_results(sampleset, prob=prob)
    log_experiment(input_name, file_name, bqm, dict_list)


def test_all_files(method, pdict=None, real_anneal_var=None):
    """Runs the annealing experiment for the files inside the inputs folder

    :param method: 'sim', 'real', 'hyb', 'cqm'
    :type method: str
    :param pdict: Dictionary containing penalty values
    :type pdict: Dict[str, float]
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]

    """
    for file in os.listdir("inputs"):
        if "init" not in file and "pycach" not in file and ".pytest_cache" not in file:
            test_single_file(file[:-3], method, pdict, real_anneal_var)


def test_single_file(
    file, method,  pdict=None, real_anneal_var=None
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
    prob = create_linear_problem(train_sets, timetable, d_max)
    annealing(prob, method, file_name, pdict, real_anneal_var)


if __name__ == "__main__":
    file = "5_trains_all_cases"
    real_anneal_var = {"num_reads": 1000, "annealing_time": 20, "chain_strength": 4}
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
    test_all_files(method, pdict = pdict) #logging not working properly
