import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

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
    cplex_t = 7.89
    cplex_obj = 188.75

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

    

    fig, (ax1,ax2,ax3) = plt.subplots(3,figsize=(6, 6),sharex=True, tight_layout= True)

    y1 = [np.mean(objectives[tmin]) for tmin in tmins]
    y2 = [np.min(objectives[tmin]) for tmin in tmins]
    y3 = [np.max(objectives[tmin]) for tmin in tmins]
    ax1.plot(tmins, y1, "o--", color = "green", label = "mean")
    ax1.plot(tmins, y2, ":", color = "green", label = "envelope")
    ax1.plot(tmins, y3, ":", color = "green")
    cplex_objs = [cplex_obj for _ in tmins]
    ax1.plot(tmins, cplex_objs, ":", color = "red", label = "CPLEX solver")
    ax1.legend(ncol = 2, loc='best')

    y1 = [np.mean(comp_time[tmin]) for tmin in tmins]
    ax2.plot(tmins, y1, "d--", color = "blue", label = "mean hybrid solver")
    cplex_ts = [cplex_t for _ in tmins]
    ax2.plot(tmins, cplex_ts, ":", color = "red", label = "CPLEX solver")
    ax2.legend(loc='best')

    y2 = [np.min(qpu_acess_time[tmin]) for tmin in tmins]
    y3 = [np.max(qpu_acess_time[tmin]) for tmin in tmins]
    ax3.plot(tmins, y2, "x--", color = "gray", label = "minimum")
    ax3.plot(tmins, y3, "d--", color = "black", label = "maximum")
    ax3.legend(loc='best', ncol = 2)
            
    ax1.set_ylabel("objective  x dmax [min]")
    ax2.set_ylabel("comp. time [s]")
    ax3.set_ylabel("QPU acess time [s]")

    ax3.set_xlabel("t min parameter")
    ax3.set_ylim(bottom=0, top = 0.04)

    plt.xscale("log")



    plt.savefig(f"{solver}_{case}_sweep_tmin.pdf")

if __name__ == "__main__":
    tmins = [5, 6, 7, 10,15,20,25,30,40, 60]
    solver = "cqm"
    case = "case7"

    plotting_objective(solver, case, tmins)