import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
k = 1

file = f"results_PULP_CBC_CMD__{k}_Integer.pkl"

results = pd.read_pickle(r'results_PULP_CBC_CMD__0_Integer.pkl')

N = results["samples"]


x = [results[i]["comp_time_seconds"] for i in range(N)]
y = [results[i]["objective"] for i in range(N)]

colors = []
colors1 = []
for i in range(N):
    if results[i]["feasible"] == True:
        colors.append("green")
        colors1.append("blue")
    else:
        colors.append("red")
        colors1.append("black")

plt.scatter(x, y, s=100, c=colors, alpha=0.5, label = "PULP_CBC_CMD")
plt.xlabel("computational time [s]")
plt.ylabel("objective times dmax [min]")
plt.legend()
#plt.show()
plt.savefig(f"case{k}.pdf")