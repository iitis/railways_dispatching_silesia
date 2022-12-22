import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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

x = [results[i]["comp_time_seconds"] for i in range(N)]
y = [results[i]["objective"] for i in range(N)]

x1 = [results1[i]["comp_time_seconds"] for i in range(N)]
y1 = [results1[i]["objective"]*results1["d_max"]-y[i] for i in range(N)]

y = [0 for _ in y]

colors = []
colors1 = []
for i in range(N):
    if results[i]["feasible"] == True:
        colors.append("green")
    else:
        colors.append("red")

for i in range(N):
    if results1[i]["feasible"] == True:
        colors1.append("blue")
    else:
        colors1.append("black")

plt.scatter(x, y, s=100, c=colors, alpha=0.5, label = f"{solver1}")
plt.scatter(x1, y1, s=100, c=colors1, alpha=0.5, label = f"{solver2}")
plt.xlabel("computational time [s]")
plt.ylabel("( objective - optimal ) x dmax [min]")
plt.legend()
plt.savefig(f"{solver1}{solver2}case{k}.pdf")