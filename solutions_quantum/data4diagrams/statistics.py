import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np


for k in [0, 4, 7]:
    data = pd.read_pickle(rf'cqm5_case{k}_Integer.pkl')

    delays = {}
    for i in range(5):
        d = data[i+1]

        for train in d:
            for s in d[train]:
                try:
                    current_delay = d[train][s]['secondary delay']
                except:
                    current_delay = ""
                


                if current_delay != "":
                    if s in delays:
                        v = delays[s]
                        v.append(current_delay)
                        delays[s] = v
                    else:
                        delays[s] = list([current_delay])


    considered_stations = ["KO(STM)", "KO", "CB", "KL", "MJ"]

    # example data
    x = considered_stations
    y = [np.mean(delays[e]) for e in considered_stations]

    p1 = 0.25
    p2 = 0.75
    y1 = [np.quantile(delays[e], p1) for e in considered_stations]
    y2 = [np.quantile(delays[e], p2) for e in considered_stations]

    fig, ax = plt.subplots(figsize=(3, 3))
    plt.subplots_adjust(left = 0.2, bottom = 0.2)

    lower_error = [np.mean(delays[e])-np.min(delays[e]) for e in considered_stations]
    upper_error = [np.max(delays[e])-np.mean(delays[e]) for e in considered_stations]
    asymmetric_error = [lower_error, upper_error]

    print()

    ax.errorbar(x, y, yerr=asymmetric_error, fmt='o',  markersize=10, label = "mean", color = "blue")
    plt.plot(x, y1, "_", markersize = 10, color = "blue", label = f"{p1}, {p2} perc.")
    plt.plot(x, y2, '_', markersize = 10, color = "blue")
    plt.ylim([-2,60])

    plt.xlabel("selected stations")
    plt.ylabel("secondary delays on departure [min]")
    plt.legend(ncol = 1)
    ax.set_title(f'case {k}')
    plt.savefig(f'statistics_case{k}.pdf')
    plt.clf()