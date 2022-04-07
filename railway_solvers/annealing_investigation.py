from pulp.constants import LpSolutionInfeasible, LpSolutionIntegerFeasible, LpStatusUndefined
from railway_solvers import *
from copy import deepcopy

"""
                                        <- 2
...............................................
 [ A ]                              .  .    [ B ]
.....................................c.........
0 ->
1 ->
"""

taus = {"pass": {"0_A_B": 4, "1_A_B": 8, "2_B_A": 8},
        "headway": {"0_1_A_B": 2, "1_0_A_B": 6},
        "stop": {"0_B": 1, "1_B": 1},
        "res": 1
        }

timetable = {"tau": taus,
             "initial_conditions": {"0_A": 4, "1_A": 1, "2_B": 8},
             "penalty_weights": {"0_A": 2, "1_A": 1, "2_B": 1}}

d_max = 10

train_sets = {
    "skip_station": {
        2: "A",  # we do not count train 2 leaving A
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": {"A": {"B": [[0, 1]]}, "B": {"A": [[2]]}},
    "Josingle": dict(),
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": dict(),
    "add_swithes_at_s": ["B"]
}

#rerouting

"""
1 ->                                       <- 2
...............................................
 [ A ]                             .   .   [ B ]
.....................................c.........
0 ->
"""


train_sets_rerouted = {
    "skip_station": {
        2: "A",
    },
    "Paths": {0: ["A", "B"], 1: ["A", "B"], 2: ["B", "A"]},
    "J": [0, 1, 2],
    "Jd": dict(),
    "Josingle": {("A", "B"): [[1,2]]},
    "Jround": dict(),
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {"A": [{1:"out", 2:"in"}], "B": [{1:"in", 2:"out"}]},
    "add_swithes_at_s": ["B"]
}

prob = create_linear_problem(train_sets, timetable, d_max)

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
