import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

k = 1
solver1 = "PULP_CBC_CMD"
solver2 = "cqm"

file = f"results_{solver1}__{k}_Integer.pkl"
results = pd.read_pickle(rf'{file}')

file1 = f"results__{solver2}_{k}_Integer.pkl"
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

#y = [0 for _ in y]

colors = []
colors1 = []
for i in range(N):
    if results[i]["feasible"] == True:
        colors.append("green")
    else:
        colors.append("red")

for i in range(N):
    if results1[i]["feasible"] == True:
        colors1.append("green")
    else:
        colors1.append("red")

print()

fig, ax = plt.subplots(figsize=(4, 3))
scatter = ax.scatter(x, y, s=100, c=colors, marker = "x",  alpha=0.5, label = f"{solver1}")
scatter1 = ax.scatter(x1, y1, s=200, c=colors1, alpha=0.5, label = f"{solver2}")
fig.subplots_adjust(bottom=0.2, left = 0.2)
plt.xlabel("computational time [min]")
plt.ylabel("objective  x dmax [min]")
if k == 1:
    plt.ylim(bottom=-25, top = 135)

legend1 = plt.legend(handles=[scatter , scatter1])

colors = ['red', 'green']
lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--', alpha=0.5) for c in colors]
labels = ['non feasible', 'feasible']
legend2 = plt.legend(lines, labels, loc = 8, fontsize = 8, ncol = 2)
ax.add_artist(legend1)
ax.add_artist(legend2)

plt.savefig(f"{solver1}_{solver2}_case{k}.pdf")