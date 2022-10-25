from typing import Tuple

import neal
import dimod
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler,
    LeapHybridSampler,
    LeapHybridCQMSampler,
)


def sim_anneal(
    bqm, beta_range=(5, 100), num_sweeps=4000, num_reads=1000
) -> dimod.sampleset.SampleSet:
    """Runs simulated annealing experiment

    :param bqm: binary quadratic model to be sampled
    :type bqm: BinaryQuadraticModel
    :param beta_range: beta range for the experiment
    :type beta_range: Tuple(int,int)
    :param num_sweeps: Number of steps
    :type num_sweeps: int
    :param num_reads: Number of samples
    :type num_reads: int
    :return: sampleset
    :rtype: dimod.SampleSet
    """
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample(
        bqm, beta_range, num_sweeps, num_reads, beta_schedule_type="geometric"
    )
    return sampleset


def real_anneal(
    bqm, num_reads, annealing_time, chain_strength
) -> dimod.sampleset.SampleSet:
    """Runs quantum annealing experiment on D-Wave

    :param bqm: binary quadratic model to be sampled
    :type bqm: BinaryQuadraticModel
    :param num_reads: Number of samples
    :type num_reads: int
    :param annealing_time: Annealing time
    :type annealing_time: int
    :param chain_strength: Chain strength parameters
    :type chain_strength: float
    :return: sampleset
    :rtype: dimod.SampleSet
    """
    sampler = EmbeddingComposite(DWaveSampler())
    # annealing time in micro second, 20 is default.
    sampleset = sampler.sample(
        bqm,
        num_reads=num_reads,
        auto_scale="true",
        annealing_time=annealing_time,
        chain_strength=chain_strength,
    )
    return sampleset


def constrained_solver(cqm) -> dimod.sampleset.SampleSet:
    """Runs experiment using constrained solver

    :param cqm: Constrained model for the problem
    :type cqm: ConstrainedQuadraticModel
    :return: sampleset
    :rtype: dimod.SampleSet
    """
    sampler = LeapHybridCQMSampler()
    return sampler.sample_cqm(cqm)


def hybrid_anneal(bqm) -> dimod.sampleset.SampleSet:
    """Runs experiment using hybrid solver

    :param bqm: Binary quadratic model for the problem
    :type bqm: BinaryQuadraticModel
    :return: sampleset
    :rtype: dimod.SampleSet
    """
    sampler = LeapHybridSampler()
    return sampler.sample(bqm)




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
    bqm, interpreter, method, real_anneal_var_dict=None, sim_anneal_var_dict=None
):
    """Performs the annealing experiment

    :param bqm: The problem instance
    :type prob: bqm
    :param interpreter: ....
    :param method: 'sim', 'real', 'hyb'
    :type method: str
    :param input_name: name of the input data
    :type input_name: str
    :param real_anneal_var_dict: Parameters for QA
    :type real_anneal_var_dict: Dict[str, float]
    """

    assert method in ["sim", "real", "hyb"]

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
    return interpreter(sampleset)
    


