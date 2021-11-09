from railway_solvers import *
from Qfile_solve import *
from mkdir import *

def annealing(prob, pdict, method, train_route, real_anneal_var_dict = None):
    """ Inputs:==
        prob: The problem,
        pdict: Dictionary of penalties
        method: 'sim', 'real',
        train_route: 'default' , 'rerouted'
        real_anneal_var_dict: dictionary containing 'num_reads', 'annealing_time' and 'chain_strength' i.e. real annealing variables
        Returns:==  Dict of feasible solution
    """

    if real_anneal_var_dict == None:
        num_reads = 1000
        annealing_time = 250
        chain_strenght = 4
    else:
        num_reads = real_anneal_var_dict['num_reads']
        annealing_time = real_anneal_var_dict['annealing_time']
        chain_strenght = real_anneal_var_dict['chain_strength']

    bqm, interpreter = convert_to_bqm(prob, pdict)
    print(f"[{train_route}]: bqm qubo size  = ", bqm.num_variables)

    file_name = f"annealing_results/bqm_{method}_anneal_{train_route}"

    if method == 'sim':
        sampleset = sim_anneal(bqm, num_sweeps=4000, num_reads = 1000)

    elif method == 'real':
        sampleset =  real_anneal(bqm, num_reads = num_reads, annealing_time = annealing_time, chain_strength = chain_strenght)

    store_result(file_name, sampleset)
    sampleset = interpreter(load_results(file_name))
    dict_list = get_results(sampleset, prob= prob)
    print(f"Best Sample {method} device", get_best_feasible_sample(dict_list))





if __name__ == "__main__":

    taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 6
                                                                    }, "stop": {"0_1": 1, "1_1": 1}, "res": 1}
    timetable = {"tau": taus,
                    "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
                    "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1}}

    d_max = 10
    μ = 30

    train_sets_default = {
        "skip_station": {
            0: [None],
            1: [None],
            2: [0],
        },
        "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
        "J": [0, 1, 2],
        "Jd": {0: {1: [[0, 1]]}, 1: {0: [[2]]}},
        "Josingle": dict(),
        "Jround": dict(),
        "Jtrack": {1: [[0, 1]]},
        "Jswitch": dict()
    }

    train_sets_rerouted = {
        "skip_station": {
            0: [None],
            1: [None],
            2: [0],
        },
        "Paths": {0: [0, 1], 1: [0, 1], 2: [1, 0]},
        "J": [0, 1, 2],
        "Jd": dict(),
        "Josingle": {(0,1): [[1,2]]},
        "Jround": dict(),
        "Jtrack": {1: [[0, 1]]},
        "Jswitch": {0: [[0, 1, 1, 2]], 1: [[0, 1, 1, 2]]}
        #"Jswitch": dict()
    }

    #WE WILL IMPORT THE ABOVE FROM OTHER FILE
    real_anneal_var = {"num_reads" : 1000, "annealing_time" : 20, "chain_strength" : 4}

    # real_anneal_var = {"num_reads" : 10, "annealing_time" : annealing_time, "chain_strength" : chain_strength}
    train_route = 'rerouted'
    method = 'sim'
    prob = create_linear_problem(eval(f"train_sets_{train_route}"), timetable, d_max, μ)
    pdict = {"minimal_span":2.5, "single_line":2.5, "minimal_stay":2.5, "track_occupation":2.5, "switch": 2.5, "occupation":2.5, "objective":1 }
    annealing(prob, pdict, method, train_route)


# for i,l in enumerate(dict_list):
#     print(l)
#     if i==100:
#         break
