from typing import KeysView
import neal
import numpy as np
from dwave.system import EmbeddingComposite, DWaveSampler, LeapHybridSampler, LeapHybridCQMSampler
import dimod
import pickle




def anneal_solutuon(method):
    if method == 'reroute':
        Q_init = np.load('files/Qfile_r.npz')
    elif method == 'default':
        Q_init = np.load('files/Qfile.npz')

    Q = Q_init['Q'].astype(np.float32)
    model = dimod.BinaryQuadraticModel.from_numpy_matrix(Q)
    qubo, offset = model.to_qubo()
    return qubo


def sim_anneal(method, beta_range=(5, 100),num_sweeps=4000, num_reads=1000):
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(anneal_solutuon(method), beta_range, num_sweeps, num_reads ,
                              beta_schedule_type='geometric')
    return sampleset


def real_anneal(method, num_reads, annealing_time, chain_strength):
    sampler = EmbeddingComposite(DWaveSampler())
    # annealing time in micro second, 20 is default.
    sampleset = sampler.sample_qubo(anneal_solutuon(method), num_reads=num_reads,
                                    auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength)
    return sampleset


def constrained_solver(method, cqm):
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm)
    return sampleset


def hybrid_anneal(method):
    sampler = LeapHybridSampler()
    sampleset = sampler.sample_qubo(anneal_solutuon(method))
    return sampleset


def store_result(file_name, sampleset):
    results = []
    for datum in sampleset.data():
        x = dimod.sampleset.as_samples(datum.sample)[0][0]
        results.append((x, datum.energy))

    sdf = sampleset.to_serializable()

    with open(file_name, 'wb') as handle:
        pickle.dump(sdf, handle)
    with open(f"{file_name}_samples", 'wb') as handle:
        pickle.dump(results, handle)

def display_results(file_name):
    print(pickle.load(open(file_name, "rb")))
    print(pickle.load(open(f"{file_name}_samples", "rb")))

def annealing_outcome(method, annealing, num_reads=None, annealing_time=None):
    """method: 'reroute', 'default',
    annealing: 'simulated', 'hybrid', 'quantum', 
    num_reads: Number of reads in quantum annealing annealing,
    annealing_time: Choose an annealing time

    returns: minimum energy/optimal solution"""

    # simulated annealing!!!!
    if annealing == 'simulated':
        sampleset = sim_anneal(method)

        results = []
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()

        with open(f"files/Qfile_complete_sol_sim-anneal_{method}", 'wb') as handle:
            pickle.dump(sdf, handle)
        with open(f"files/Qfile_samples_sol_sim-anneal_{method}", 'wb') as handle:
            pickle.dump(results, handle)

        print(f"Simulated solver energy {results[0]}")
        # hybrid annealing!!!
    elif annealing == 'hybrid':
        sampleset = hybrid_anneal(method)

        results = []
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()

        with open(f"files/hybrid_data/Qfile_complete_sol_hybrid-anneal_{method}", 'wb') as handle:
            pickle.dump(sdf, handle)
        with open(f"files/hybrid_data/Qfile_samples_sol_hybrid-anneal_{method}", 'wb') as handle:
            pickle.dump(results, handle)
        # print(f"Hybrid solver energy {results}")

    # quantum annealing!!!!!
    elif annealing == 'quantum':
        for chain_strength in [3, 3.5, 4, 4.5]:
            sampleset = real_anneal(
                method, num_reads, annealing_time, chain_strength)

            results = []
            for datum in sampleset.data():
                x = dimod.sampleset.as_samples(datum.sample)[0][0]
                results.append((x, datum.energy))

            sdf = sampleset.to_serializable()

            with open(f"files/dwave_data/Qfile_complete_sol_real-anneal_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}_{method}", 'wb') as handle:
                pickle.dump(sdf, handle)
            with open(f"files/dwave_data/Qfile_samples_sol_real-anneal_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}_{method}", 'wb') as handle:
                pickle.dump(results, handle)

            # print(f"Energy {sampleset.first} with chain strength {chain_strength} run")
