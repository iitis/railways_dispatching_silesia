from typing import KeysView
import neal
import numpy as np
from dwave.system import EmbeddingComposite, DWaveSampler, LeapHybridSampler
import dimod
import pandas as pd
#import dwave.inspector
import pickle
# from edge_helpers import *
# from generate_ham_edge import *
# from generate_ham_ilp import *
# from ilp_helpers import *



def anneal_solutuon(method):

    if method == 'reroute':
        Q_init = np.load('files/Qfile_r.npz')
    elif method == 'default':
        Q_init = np.load('files/Qfile.npz')
    
    Q = Q_init['Q'].astype(np.float32)
    model = dimod.BinaryQuadraticModel.from_numpy_matrix(Q)
    qubo, offset = model.to_qubo()
    return qubo

def sim_anneal(method):

    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(anneal_solutuon(method), beta_range=(5,100), num_sweeps=4000, num_reads=1000,
                               beta_schedule_type='geometric')
    return sampleset


def real_anneal(method, num_reads, annealing_time, chain_strength):
    sampler = EmbeddingComposite(DWaveSampler())
    sampleset = sampler.sample_qubo(anneal_solutuon(method), num_reads=num_reads, auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength) #annealing time in micro second, 20 is default.
    return sampleset

def hybrid_anneal(method):
    sampler = LeapHybridSampler()
    sampleset = sampler.sample_qubo(anneal_solutuon(method))
    return sampleset


def annealing_outcome(method, annealing, num_reads = None, annealing_time = None):
    """method: 'reroute', 'default',
    annealing: 'simulated', 'hybrid', 'quantum', 
    num_reads: Number of reads in quantum annealing annealing,
    annealing_time: Choose an annealing time
    
    returns: minimum energy/optimal solution"""
    
    #simulated annealing!!!!
    if annealing == 'simulated':

        sampleset = sim_anneal(method)
        
        results=[]
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()

        with open("files/Qfile_complete_sol_sim-anneal_{}".format(method), 'wb') as handle:
            pickle.dump(sdf, handle)
        with open("files/Qfile_samples_sol_sim-anneal_{}".format(method), 'wb') as handle:
            pickle.dump(results, handle)
        
        print('Simulated solver energy {}'.format(results[0]))

    
    #hybrid annealing!!!
    elif annealing == 'hybrid':

        sampleset = hybrid_anneal(method)
        
        results = []
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()

        with open("files/hybrid_data/Qfile_complete_sol_hybrid-anneal_{}".format(method), 'wb') as handle:
            pickle.dump(sdf, handle)
        with open("files/hybrid_data/Qfile_samples_sol_hybrid-anneal_{}".format(method), 'wb') as handle:
            pickle.dump(results, handle)
        
        # print('Hybrid solver energy {}'.format(results))
        

    #quantum annealing!!!!!
    elif annealing == 'quantum':
        for chain_strength in [3,3.5,4,4.5]:
        
            sampleset = real_anneal(method, num_reads, annealing_time, chain_strength)
            
            results=[]
            for datum in sampleset.data():
                x = dimod.sampleset.as_samples(datum.sample)[0][0]
                results.append((x, datum.energy))

            sdf = sampleset.to_serializable()

            with open("files/dwave_data/Qfile_complete_sol_real-anneal_numread{}_antime{}_chainst{}_{}".format(num_reads, annealing_time,chain_strength,method), 'wb') as handle:
                pickle.dump(sdf, handle)
            with open("files/dwave_data/Qfile_samples_sol_real-anneal_numread{}_antime{}_chainst{}_{}".format(num_reads, annealing_time,chain_strength, method), 'wb') as handle:
                pickle.dump(results, handle)
        


            # print('Energy {} with chain strength {} run'.format(sampleset.first, chain_strength))


if __name__ == "__main__":
    import sys

    sys.path.append('../files')
    print(annealing_outcome('reroute','simulated'))