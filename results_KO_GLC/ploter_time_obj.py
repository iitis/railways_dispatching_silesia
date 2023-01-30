"""plots computational results from KO-GLC  generic cases"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

case = 1
solver1 = "PULP_CBC_CMD"
#solver1 = "CPLEX_CMD"
solver2 = "cqm"

file = f"results_{solver1}__{case}_Integer.pkl"
results = pd.read_pickle(rf'{file}')

file1 = f"results__{solver2}_{case}_Integer.pkl"
results1 = pd.read_pickle(rf'{file1}')
N = results1["samples"]

int_vars = [results[i]["int_vars"] for i in range(N)]
order_vars = [results[i]["order_vars"] for i in range(N)]
constraints = [results[i]["constraints"] for i in range(N)]

print("mean n.o. int vars", np.mean(int_vars))
print("mean n.o. order vars", np.mean(order_vars))
print("mean n.o. constraints", np.mean(constraints))

x = [results[i]["comp_time_seconds"]/60 for i in range(N)]
y = [results[i]["objective"] for i in range(N)]

x1 = [results1[i]["comp_time_seconds"]/60 for i in range(N)]
y1 = [results1[i]["objective"]*results1["d_max"] for i in range(N)]


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

fig, ax = plt.subplots(figsize=(6, 2))
scatter = ax.scatter(instance, y, s=20, c=colors, marker = "x",  alpha=0.5, label = f"{solver1}")
scatter1 = ax.scatter(instance, y1, s=40, c=colors1, alpha=0.5, label = f"{solver2}")
fig.subplots_adjust(bottom=0.2, left = 0.2)
plt.xlabel("instance")
plt.ylabel("objective  x dmax [min]")
plt.ylim(bottom=-25)


legend_elements = [Line2D([0], [0], marker='x', color='g', label=f"{solver1}", linewidth = 0.,
                          markerfacecolor='g', markersize=5, alpha=0.5),
                   Line2D([0], [0], marker='o', color='g', label=f"{solver2}", linewidth = 0.,
                          markerfacecolor='g', markersize=5, alpha=0.5)]

legend0 = plt.legend(handles=legend_elements)

col = ['red', 'green']
lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--', alpha=0.5) for c in col]
labels = ['non feasible', 'feasible']
if case == 2:
    legend2 = plt.legend(lines, labels, loc = 3, fontsize = 8, ncol = 2)
else:
    legend2 = plt.legend(lines, labels, loc = 4, fontsize = 8, ncol = 2)
ax.add_artist(legend0)
ax.add_artist(legend2)

plt.savefig(f"{solver1}_{solver2}_obj_case{case}.pdf")


fig, ax = plt.subplots(figsize=(6, 2))
scatter = ax.scatter(instance, x, s=20, c=colors, marker = "x",  alpha=0.5, label = f"{solver1}")
scatter1 = ax.scatter(instance, x1, s=40, c=colors1, alpha=0.5, label = f"{solver2}")
fig.subplots_adjust(bottom=0.2, left = 0.2)
plt.xlabel("instance")
plt.ylabel("comp. time [min]")
legend0 = plt.legend(handles=legend_elements)

ax.add_artist(legend0)


plt.savefig(f"{solver1}_{solver2}_compt_case{case}.pdf")