import neal
from dwave.system import EmbeddingComposite, DWaveSampler, LeapHybridSampler, LeapHybridCQMSampler




def sim_anneal(bqm, beta_range=(5, 100), num_sweeps=4000, num_reads=1000):
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample(bqm, beta_range, num_sweeps, num_reads,
                         beta_schedule_type='geometric')
    return sampleset


def real_anneal(bqm, num_reads, annealing_time, chain_strength):
    sampler = EmbeddingComposite(DWaveSampler())
    # annealing time in micro second, 20 is default.
    sampleset = sampler.sample(bqm, num_reads=num_reads,
                               auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength)
    return sampleset


def constrained_solver(cqm):
    sampler = LeapHybridCQMSampler()
    return sampler.sample_cqm(cqm)


def hybrid_anneal(bqm):
    sampler = LeapHybridSampler()
    return sampler.sample_qubo(bqm)
