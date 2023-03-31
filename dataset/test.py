import json

# f = "/Users/jiahong/Downloads/coqa-train-v1.0.json"
#
# data = json.load(open(f))
#
# print(json.dumps(data['data'][0]))

f = "/Users/jiahong/Downloads/personality.csv"

import pandas as pd

df = pd.read_csv(f)
print(df.head())
print(df.values[:2])
