import pandas as pd

k = 4   # 5,7,8

data = pd.read_pickle(rf'cqm5_case{k}_Integer.pkl')


d = data[1]["sample"]

keys = list(filter(lambda x: "Delay" in x, d))

print([(key, d[key]) for key in keys])

