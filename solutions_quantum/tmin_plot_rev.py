import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D

import matplotlib as mpl
mpl.rcParams.update(mpl.rcParamsDefault)

plt.rcParams.update(
    {"text.usetex": True, "font.family": "serif", "font.size": 11}
)


def load_data(solver,case, tmin):
    file = f"{solver}{tmin}_{case}_Integer.pkl"
    results = pd.read_pickle(rf'{file}')
    return results

markers = ["o", "x", "*", "^", "^", "d", "v", "s", "*", "^"]

def plotting_objective(solver, case, tmins):
    dmax = 40
    if case == "case7":
        cplex_t = 7.89
        cplex_obj = 188.75
    if case == "case9":
        cplex_t = 6.51
        cplex_obj = 185.5

    objectives = {}
    comp_time = {}
    qpu_acess_time = {}
    for tmin in tmins:
        data = load_data(solver,case, tmin)
        objectives[tmin] = [data[i+1]["objective"]*dmax for i in range(len(data))]
        comp_time[tmin] = [data[i+1]["info"]["run_time"]/1000000 for i in range(len(data))]
        qpu_acess_time[tmin] = [data[i+1]["info"]["qpu_access_time"]/1000000 for i in range(len(data))]

        # checks feasibility of all solutions
        assert np.prod([data[i+1]["feasible"] for i in range(len(data))]) == 1

    

    _, (ax1) = plt.subplots(1,figsize=(3.1, 2.8),sharex=True, tight_layout= True)

    y1 = [np.mean(objectives[tmin]) for tmin in tmins]
    y2 = [np.min(objectives[tmin]) for tmin in tmins]
    y3 = [np.max(objectives[tmin]) for tmin in tmins]

    ct = [np.mean(comp_time[tmin]) for tmin in tmins]


    ax1.plot(ct, y1, "o", color = "green", label = "mean")
    ax1.plot(ct, y2, ":", color = "green", label = "env.")
    ax1.plot(ct, y3, ":", color = "green")
    a, b = np.polyfit(np.log(ct), y1, 1)

    c = case.replace("case", "")
    

    if case == "case7":
        ax1.set_title("disturbence 1")
    elif case == "case9":
        ax1.set_title("disturbance 2")

    ax1.plot(ct, a*np.log(ct)+b, "--", color = "green", label = "log lin. fit")


    ax1.set_ylim(bottom = 0, top = 300)
    
    y1 = [np.mean(comp_time[tmin]) for tmin in tmins]


    cplex_objs = [cplex_obj for _ in tmins]
    
    ax1.plot([cplex_t], [cplex_obj], "o", color = "black", label = "CPLEX")
    ax1.plot(tmins, cplex_objs, ":", color = "black", label = "Optimum")

    ax1.legend(ncol = 2, loc=3, fontsize = 9)

    ax1.set_ylabel("objective [min]")

    ax1.set_xlabel("comp time [s]")


    plt.xscale("log")
    ax1.set_xticks([5,10,50])
    ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())



    plt.savefig(f"{solver}_{case}_R_tmin.pdf")

if __name__ == "__main__":
    tmins = [5, 6, 7, 10,15,20,25,30,40, 60]
    solver = "cqm"
    for case in ["case7", "case9"]:
        plotting_objective(solver, case, tmins)