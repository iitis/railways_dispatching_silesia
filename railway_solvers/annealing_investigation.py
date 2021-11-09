from pulp.constants import LpSolutionInfeasible, LpSolutionIntegerFeasible, LpStatusUndefined
from railway_solvers import *
from copy import deepcopy
taus = {"pass": {"0_0_1": 4, "1_0_1": 8, "2_1_0": 8}, "blocks": {"0_1_0_1": 2, "1_0_0_1": 6
                                                                }, "stop": {"0_1": 1, "1_1": 1}, "res": 1}

timetable = {"tau": taus,
                "initial_conditions": {"0_0": 4, "1_0": 1, "2_1": 8},
                "penalty_weights": {"0_0": 2, "1_0": 1, "2_1": 1}}

d_max = 10
μ = 30

train_sets = {
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

prob = create_linear_problem(train_sets, timetable, d_max, μ)

import pickle
import io
data = pickle.load(open("annealing_results/cqm_default", 'rb'))
# print(data)
print(data.keys())
print(data['sample_data']['data'][0])
print(len(data['sample_data']['data']))
print(data['variable_labels'])
print(len(data['vectors']['is_satisfied']['data']))
print(data['vectors'].keys())
print(data['num_rows'])

cqm, interpreter = convert_to_cqm(prob)
interpreted_data = interpreter(data)

out = results_to_dict(interpreted_data, mode="cqm")
print(analyze_constraints(prob, out[1]))
print('----------')
for i in range(50):
    print(get_objective(prob, out[i]), is_feasible(prob, out[i]))
# final_data = []
# for i in range(data['num_rows']):
#     prob_tmp = deepcopy(prob)
#     if all(data['vectors']['is_satisfied']['data'][i]):
#         prob_tmp.status = LpStatusUndefined
#         prob_tmp.sol_status = LpSolutionInfeasible
#     else:
#         prob_tmp.status = LpStatusUndefined
#         prob_tmp.sol_status = LpSolutionIntegerFeasible

#     values = {var:val for val, var in zip(data['sample_data']['data'][0], data['variable_labels'])}
#     prob_tmp.assignVarsVals(values)
#     final_data.append(prob_tmp)
# print(final_data[0].variablesDict()['Delays_0_0'].__dict__())
