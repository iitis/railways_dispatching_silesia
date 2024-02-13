import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import numpy as np


def add_delays_one_realisation(delays, d):
    """ append delays to dict indexed by station """
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

def get_print_statistics(delays, considered_stations):
    """ computes returns and pronts statistics of delays """
    means = [np.mean(delays[e]) for e in considered_stations]
    q25 = [np.quantile(delays[e], 0.25) for e in considered_stations]
    q75 = [np.quantile(delays[e], 0.75) for e in considered_stations]
    minimum = [np.min(delays[e]) for e in considered_stations]
    maximum = [np.max(delays[e]) for e in considered_stations]


    print("stations", considered_stations)
    print("max delay", maximum)
    print("quantile 75", q75)
    print("mean", means)
    print("quantile 25", q25)
    print("min", minimum)

    return q25, means, q75

def plot_stats(delays, q25, means, q75, name, color):
    if k in [0, 4,7]:

        lower_error = [np.mean(delays[e])-np.min(delays[e]) for e in considered_stations]
        upper_error = [np.max(delays[e])-np.mean(delays[e]) for e in considered_stations]
        asymmetric_error = [lower_error, upper_error]
        _, ax = plt.subplots(figsize=(3, 3))
        plt.subplots_adjust(left = 0.2, bottom = 0.2)
        ax.errorbar(considered_stations, means, yerr=asymmetric_error, fmt='o',  markersize=10, label = "mean", color = color)
        plt.plot(considered_stations, q25, "_", markersize = 10, color = color, label = "0.25, 0.75 perc.")
        plt.plot(considered_stations, q75, '_', markersize = 10, color = color)
        plt.ylim([-2,60])
        plt.xlabel("selected stations")
        plt.ylabel("secondary delays on departure [min]")
        plt.legend(ncol = 1)
        ax.set_title(f'network {k}')
        plt.savefig(f'{name}_case{k}.pdf')
        plt.clf()

if __name__ == "__main__":
    print("........... hybrid  ..............")
    for k in range(10):
        data = pd.read_pickle(rf'cqm5_case{k}_Integer.pkl')
        delays = {}
        for keys in data:
            add_delays_one_realisation(delays, data[keys])
        considered_stations = ["KO(STM)", "KO", "CB", "KL", "MJ"]


        print("case", k)
        q25, means, q75 = get_print_statistics(delays, considered_stations)   
        plot_stats(delays, q25, means, q75, "statistics", "blue")
        

    print(".............  clasical .................")
    for k in range(10):
        data = pd.read_pickle(rf'PULP_CBC_CMD_case{k}_Integer.pkl')
        delays = {}
        add_delays_one_realisation(delays, data)
        considered_stations = ["KO(STM)", "KO", "CB", "KL", "MJ"]

        print("case", k)
        q25, means, q75 = get_print_statistics(delays, considered_stations)  
        plot_stats(delays, q25, means, q75, "classical_statistics", "red")