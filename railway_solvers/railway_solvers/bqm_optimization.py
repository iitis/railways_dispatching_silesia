from typing import Tuple
import os

from .converter_bqm import convert_to_bqm
from .converter_cqm import convert_to_cqm
from .Qfile_solve import sim_anneal, real_anneal, constrained_solver, hybrid_anneal
from .results_manipulation import get_results, get_best_feasible_sample

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

def process_experiment(bqm, dict_list):
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

    print("------------------------new run---------------------")

    print(f"Number of variables: {len(bqm.variables)}")
    sample = get_best_feasible_sample(dict_list)
    if sample != None:
        feasible = sample["feasible"]
        energy = sample["energy"]
        objective = sample["objective"]
        print(f"Best Sample energy, {energy}, objective, {objective}, feasible, {feasible}")
        print("Samples:")
    else:
        print(None)
    return sample

        
def annealing(
    prob, method, pdict=None, real_anneal_var_dict=None, sim_anneal_var_dict=None, file_name =None
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
    if method == "cqm":
        cqm, interpreter = convert_to_cqm(prob)
        sampleset = constrained_solver(cqm)
    else:
        bqm, _, interpreter = convert_to_bqm(prob, pdict)
        if method == "sim":
            sampleset = sim_anneal(bqm, beta_range=sim_anneal_var_dict["beta_range"], num_sweeps=sim_anneal_var_dict["num_sweeps"], num_reads=sim_anneal_var_dict["num_reads"])
        elif method == "real":
            num_reads, annealing_time, chain_strength = get_parameters(
                real_anneal_var_dict
            )
            sampleset = real_anneal(
                bqm,
                num_reads=num_reads,
                annealing_time=annealing_time,
                chain_strength=chain_strength,
            )
        elif method == "hyb":
            sampleset = hybrid_anneal(bqm)

    #store_result(file_name, sampleset)
    #load_results(file_name)
    sampleset = interpreter(sampleset)
    dict_list = get_results(sampleset, prob=prob)
    return process_experiment(bqm, dict_list)



