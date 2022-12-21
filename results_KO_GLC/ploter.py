import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
k = 1

file = f"results_PULP_CBC_CMD__{k}_Integer.pkl"
results = pd.read_pickle(rf'{file}')

file1 = f"results_PULP_CBC_CMD__{k}_Integer.pkl"
results1 = pd.read_pickle(rf'{file}')
N = results1["samples"]


x = [results[i]["comp_time_seconds"] for i in range(N)]
y = [results[i]["objective"] for i in range(N)]

x1 = [results1[i]["comp_time_seconds"] for i in range(N)]
y1 = [results1[i]["objective"] for i in range(N)]

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

plt.scatter(x, y, s=100, c=colors, alpha=0.5, label = "PULP_CBC_CMD")
plt.scatter(x1, y1, s=100, c=colors, alpha=0.5, label = "quantum sim")
plt.xlabel("computational time [s]")
plt.ylabel("objective times dmax [min]")
plt.legend()
plt.savefig(f"case{k}.pdf")