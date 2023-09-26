""" helpers for close to real and generic examples """
import pickle as pkl
import numpy as np
import pandas as pd
import pytest
import time

from data_formatting.data_formatting import (
    get_initial_conditions,
    get_J,
    get_jround,
    get_Paths,
    get_schedule,
    get_taus_headway,
    get_taus_pass,
    get_taus_prep,
    get_taus_stop,
    jd,
    josingle,
    jswitch,
    jtrack,
    make_weights,
    timetable_to_train_dict,
    update_all_timetables,
)
from railway_solvers.railway_solvers import (
    delay_and_acctual_time,
    impact_to_objective,
    sim_anneal,
    real_anneal,
    hybrid_anneal,
    get_results,
    get_best_feasible_sample,
    convert_to_cqm,
    constrained_solver,
    convert_to_bqm
)

def load_timetables(timetables_path):
    with open(timetables_path.load, "rb") as file:
        train_dict = pkl.load(file)
    return train_dict

def load_important_stations(important_station_path):
    return np.load(important_station_path, allow_pickle=True)["arr_0"][()]

def load_data_paths(data_paths_path):
    return pd.read_excel(data_paths_path, engine="odf")

def build_timetables(d, save, important_stations, data_paths):
    data = pd.read_csv(d, sep=";", engine="python")
    train_dicts = timetable_to_train_dict(data)
    train_dicts = update_all_timetables(
        train_dicts, data_paths, important_stations, save=save
    )
    return train_dicts

def make_taus(train_dict, important_stations, r):
    taus = {}
    taus["pass"] = get_taus_pass(train_dict, r=r)
    taus["headway"] = get_taus_headway(train_dict, important_stations, r=r)
    taus["prep"] = get_taus_prep(train_dict, important_stations, r=r)
    taus["stop"], prep_extra = get_taus_stop(train_dict, important_stations, r=r)
    taus["prep"].update(prep_extra)
    taus["res"] = 1
    return taus

def make_timetable(
    train_dict, important_stations, skip_stations, t1="16:00", taus=None
):
    timetable = {}
    if taus is None:
        taus = make_taus(train_dict, important_stations, 1)
    timetable["tau"] = taus
    timetable["initial_conditions"] = get_initial_conditions(train_dict, t1)
    timetable["penalty_weights"] = make_weights(
        train_dict, skip_stations, stopping=1, fast=1.5, express=1.75, empty=0
    )
    timetable["schedule"] = get_schedule(train_dict, t1)
    return timetable

def make_train_set(train_dict, important_stations, data_path, skip_stations):
    train_set = {}
    train_set["skip_station"] = skip_stations
    train_set["Paths"] = get_Paths(train_dict)
    train_set["J"] = get_J(train_dict)
    train_set["Jd"] = jd(train_dict, important_stations)
    train_set["Josingle"] = josingle(train_dict, important_stations)
    train_set["Jround"] = get_jround(train_dict, important_stations)
    train_set["Jtrack"] = jtrack(train_dict, important_stations)
    train_set["Jswitch"] = jswitch(train_dict, important_stations, data_path)
    return train_set

def print_optimisation_results(prob, timetable, train_set, skip_stations, d_max, t_ref, outside_data = []):
    print("xxxxxxxxxxx  OUTPUT TIMETABLE  xxxxxxxxxxxxxxxxx")
    print("reference_time", t_ref)
    for j in train_set["J"]:
        print("..............")
        print("train", j)
        for s in train_set["Paths"][j]:
            if j in skip_stations and s == skip_stations[j]: 
                0
            else:
                delta_obj = impact_to_objective(prob, timetable, j, s, d_max, outside_data)
                delay, conflict_free, conflicted_tt = delay_and_acctual_time(
                    train_set, timetable, prob, j, s, outside_data
                )
                try:
                    sched = timetable["schedule"][f"{j}_{s}"]
                    print("s",
                        s,
                        "v", 
                        int(conflicted_tt),
                        "d",
                        int(delay),
                        "t",
                        int(conflict_free),
                        "delta f(t)",
                        delta_obj,
                        "||",
                        "schedule",
                        sched,
                    )
                except:
                    print("s",
                        s,
                        "v", 
                        int(conflicted_tt),
                        "d",
                        int(delay),
                        "t",
                        int(conflict_free),
                        "delta f(t)",
                        delta_obj,
                    )

def check_count_vars(prob):
    """
    counts n.o. vars and checks if bool vars are 0 or 1
    """
    order_vars = 0
    for v in prob.variables():
        if "z_" in str(v) or "y_" in str(v):
            assert v.varValue in [pytest.approx(0), pytest.approx(1)]
            order_vars += 1
    int_vars = len(prob.variables()) - order_vars
    constraints = prob.numConstraints()
    print("....  linear problem size ....")
    print("n.o. order vars = ", order_vars)
    print("n.o. integer vars = ", int_vars)
    print("n.o. linear constraints = ", constraints)



def count_vars(prob):
    """
    counts n.o. vars and checks  
    """
    order_vars = 0
    for v in prob.variables():
        if "z_" in str(v) or "y_" in str(v):
            order_vars += 1
    int_vars = len(prob.variables()) - order_vars
    constraints = prob.numConstraints()
    return order_vars, int_vars, constraints


# Solving on quantum

def q_process(prob, method, pdict, minimum_time_limit):
    """actual set of quantum solvers, 
    
    input

    prob: linear problem ILP
    method: string in ["sim", "real", "bqm", "cqm"]
    pdict: a dict of parameters for QUBO creation for ["sim", "real", "bqm"]
    minimum_time_limit: parameter for hybrid solvers

    returns set of samples (sampleset)  properties, info  (information from solver)

    """


    if method in ["sim", "real", "bqm"]:
        bqm, _, interpreter = convert_to_bqm(prob, pdict)
    else:
        cqm = convert_to_cqm(prob)

    if method == "sim":
        beta_range=(0.001, 10)
        num_sweeps=10
        num_reads=2
        #beta_range=(0.00001, 100)
        #num_sweeps=1000
        #num_reads=1000

        sampleset = sim_anneal(bqm, beta_range=beta_range, num_sweeps=num_sweeps, num_reads=num_reads)  
        properties = {"beta_range":beta_range, "num_sweeps":num_sweeps, "num_reads":num_reads}
        interpreted_sampleset = interpreter(sampleset)

    elif method  == "real":
        sampleset = real_anneal(bqm,num_reads=1000, annealing_time=250, chain_strength=4)
        properties = ""
        interpreted_sampleset = interpreter(sampleset)
        
    elif method  == "bqm":
        sampleset, properties = hybrid_anneal(bqm, minimum_time_limit = minimum_time_limit)
        interpreted_sampleset = interpreter(sampleset)
        
    elif method == "cqm":
        sampleset, properties = constrained_solver(cqm, minimum_time_limit = minimum_time_limit)
        interpreted_sampleset = sampleset

    
    return interpreted_sampleset, properties, sampleset.info


def solve_on_quantum(prob, method, pdict, minimum_time_limit):
    """solve given problem on various quantum / hybrid algorithms
    
        prob: linear problem ILP
    method: string in ["sim", "real", "bqm", "cqm"]
    pdict: a dict of parameters for QUBO creation for ["sim", "real", "bqm"]
    minimum_time_limit: parameter for hybrid solvers

    returns sample dict of solutions with parameters and measured comp times
    """

    start_time = time.time()

    interpreted_sampleset, properties, info = q_process(prob, method, pdict, minimum_time_limit)

    t = time.time() - start_time

    print("measured comp time",t)
    dict_list = get_results(interpreted_sampleset, prob=prob)
    sample = get_best_feasible_sample(dict_list)
    print("end results analysis")
    sample.update({"comp_time_seconds": t})
    sample.update({"info": info})
    sample.update({"properties": properties})
    print("feasible", sample["feasible"])
    print("objective", sample["objective"])

    print("xxxxxxxxxxxxxxxxxxxxxxx")

    return sample