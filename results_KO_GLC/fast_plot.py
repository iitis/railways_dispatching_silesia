import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

plt.rcParams.update(
    {"text.usetex": True, "font.family": "serif", "font.size": 11}
)


def load_data(solver,case):
    file = f"results_{solver}__{case}_Integer.pkl"
    results = pd.read_pickle(rf'{file}')
    return results

markers = ["o", "x", "*", "^", "^", "d", "v", "s", "*", "^"]
sizes = [40,60,60,40,40]

def plotting_comparisons(c_solvers,cases, dict_times):
    q_solver = "cqm"

    for case in cases:
        times = dict_times[case]
        for solver in c_solvers:
            fig, (ax1,ax2,ax3) = plt.subplots(3,figsize=(6, 6),sharex=True, tight_layout= True)
            for t,m,s in zip(times,markers, sizes): 
                file = f"results{t}__{q_solver}_{case}_Integer.pkl"
                results1 = pd.read_pickle(rf'{file}')
                N = results1["samples"]
                x1 = [results1[i]["comp_time_seconds"]/60 for i in range(N)]
                y1 = [results1[i]["objective"]*results1["d_max"] for i in range(N)]
                x2 = [results1[i]["info"]["qpu_access_time"]/1000000 for i in range(N)]
                    
                instance = [i for i in range(N)]

                colors1 = []
                label2 = q_solver.upper() + " t\_min =" f" {t}"
                for i in range(N):
                    if results1[i]["feasible"] is True:
                        colors1.append("green")
                    else:
                        colors1.append("red")
                        # label2 = "_"

                    
                ax1.scatter(instance, y1, s=s, marker = m, c=colors1, alpha=0.5, label = f"{label2}")
                ax2.scatter(instance, x1, s=s, marker = m, c=colors1, alpha=0.5, label = f"{label2}")
                ax3.scatter(instance, x2, s=s, marker = m, c=colors1, alpha=0.5, label = f"{label2}")


                
            results = load_data(solver,case)

            int_vars = [results[i]["int_vars"] for i in range(N)]
            order_vars = [results[i]["order_vars"] for i in range(N)]
            constraints = [results[i]["constraints"] for i in range(N)]

            print("mean n.o. int vars", np.mean(int_vars))
            print("mean n.o. order vars", np.mean(order_vars))
            print("mean n.o. constraints", np.mean(constraints))
            
            x = [results[i]["comp_time_seconds"]/60 for i in range(N)]
            y = [results[i]["objective"] for i in range(N)]

            colors = []
            for i in range(N):
                if results[i]["feasible"] is True:
                    colors.append("green")
                else:
                    colors.append("red")
            
            label1 = solver.replace("_"," ")
            
            ax1.plot(instance, y, c="green", marker = "*", linestyle= ":",  alpha=0.25, label = f"{label1}")
            ax1.scatter(instance, y, s=40, c=colors, marker = "*",  alpha=0.25)
            
            fig.subplots_adjust(bottom=0.2, left = 0.2)
            # plt.xlabel("instance")
            ax1.set_ylabel("objective  x dmax [min]")
            #ax1.set_ylim(bottom=-25)
            ax3.set_ylim(bottom=0, top = 0.04)

            ax2.plot(instance, x, c="green", marker = "*", linestyle= ":",  alpha=0.5, label = f"{label1}")
            ax2.scatter(instance, x, s=40, c=colors, marker = "*",  alpha=0.25)
            fig.subplots_adjust(bottom=0.2, left = 0.2)
            ax3.set_xlabel("instance")
            ax2.set_ylabel("comp. time [min]")
            ax3.set_ylabel("QPU acess time [s]")

            ax2.legend(ncol = 2, loc='best')

            #ax2.legend(ncol = 2)
            #ax3.legend()


            plt.savefig(f"{solver}_{q_solver}_compt_case{case}b.pdf")

if __name__ == "__main__":
    cases = list(range(1,4))
    c_solvers = [r"CPLEX_CMD"]
    dict_times = {1: [5, 20], 2:[5, 20], 3: [5,20]}


    plotting_comparisons(c_solvers,cases,dict_times)