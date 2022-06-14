from pulp.constants import LpSolutionInfeasible, LpSolutionIntegerFeasible, LpStatusUndefined
from railway_solvers import create_linear_problem, convert_to_cqm, interpreter
from railway_solvers import analyze_constraints, is_feasible
from copy import deepcopy

import os
import logging
import importlib


file = "HOBO_case_default"
file_name = f"inputs.{file}"
mdl = importlib.import_module(file_name)
globals().update(mdl.__dict__)

prob = create_linear_problem(train_sets, timetable, d_max)

import pickle
import io
data = pickle.load(open("annealing_results/inputs.HOBO_case_default/sim", 'rb'))
# print(data)
print(data.keys())
print(data['sample_data']['data'][0])
print(len(data['sample_data']['data']))
print(data['variable_labels'])
#print(len(data['vectors']['is_satisfied']['data']))
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
