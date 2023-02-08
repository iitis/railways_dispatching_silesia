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


def plotting_comparisons(c_solvers,cases):
    q_solver = "cqm"
    for case in cases:    
        file = f"results__{q_solver}_{case}_Integer.pkl"
        results1 = pd.read_pickle(rf'{file}')
        N = results1["samples"]
        x1 = [results1[i]["comp_time_seconds"]/60 for i in range(N)]
        y1 = [results1[i]["objective"]*results1["d_max"] for i in range(N)]

        for solver in c_solvers:
            results = load_data(solver,case)

            int_vars = [results[i]["int_vars"] for i in range(N)]
            order_vars = [results[i]["order_vars"] for i in range(N)]
            constraints = [results[i]["constraints"] for i in range(N)]

            print("mean n.o. int vars", np.mean(int_vars))
            print("mean n.o. order vars", np.mean(order_vars))
            print("mean n.o. constraints", np.mean(constraints))
            
            x = [results[i]["comp_time_seconds"]/60 for i in range(N)]
            y = [results[i]["objective"] for i in range(N)]

            instance = [i for i in range(N)]

            colors = []
            colors1 = []
            for i in range(N):
                if results[i]["feasible"] is True:
                    colors.append("green")
                else:
                    colors.append("red")

            for i in range(N):
                if results1[i]["feasible"] is True:
                    colors1.append("green")
                else:
                    colors1.append("red")

            print()
            label2 = q_solver.upper()
            label1 = solver.replace("_"," ")
            fig, (ax1,ax2) = plt.subplots(2,figsize=(6, 4),sharex=True, tight_layout= True)
            scatter = ax1.scatter(instance, y, s=20, c=colors, marker = "x",  alpha=0.5, label = f"{label1}")
            scatter1 = ax1.scatter(instance, y1, s=40, c=colors1, alpha=0.5, label = f"{label2}")
            fig.subplots_adjust(bottom=0.2, left = 0.2)
            # plt.xlabel("instance")
            ax1.set_ylabel("objective  x dmax [min]")
            ax1.set_ylim(bottom=-25)


            legend_elements = [Line2D([0], [0], marker='x', color='g', label=f"{label1}", linewidth = 0.,
                                    markerfacecolor='g', markersize=5, alpha=0.5),
                            Line2D([0], [0], marker='o', color='g', label=f"{label2}", linewidth = 0.,
                                    markerfacecolor='g', markersize=5, alpha=0.5)]

            ax1.legend(handles=legend_elements)

            col = ['red', 'green']
            lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--', alpha=0.5) for c in col]
            #labels = ['non feasible', 'feasible']
            #if case == 2:
            #    legend2 = plt.legend(lines, labels, loc = 3, fontsize = 8, ncol = 2)
            #else:
            #    legend2 = plt.legend(lines, labels, loc = 4, fontsize = 8, ncol = 2)
            # ax1.add_artist(legend0)
            #ax.add_artist(legend2)

            # plt.savefig(f"{solver1}_{solver2}_obj_case{case}.pdf")


            # fig, ax = plt.subplots(figsize=(6, 2))
            scatter = ax2.scatter(instance, x, s=20, c=colors, marker = "x",  alpha=0.5, label = f"{label1}")
            scatter1 = ax2.scatter(instance, x1, s=40, c=colors1, alpha=0.5, label = f"{label2}")
            fig.subplots_adjust(bottom=0.2, left = 0.2)
            ax2.set_xlabel("instance")
            ax2.set_ylabel("comp. time [min]")
            ax2.legend(handles=legend_elements)

            plt.savefig(f"{solver}_{q_solver}_compt_case{case}b.pdf")

if __name__ == "__main__":
    cases = list(range(1,4))
    c_solvers = [r"PULP_CBC_CMD",r"CPLEX_CMD"]

    plotting_comparisons(c_solvers,cases)