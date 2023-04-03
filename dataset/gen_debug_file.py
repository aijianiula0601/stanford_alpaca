import pandas as pd
import csv
from pathlib import Path
import json
import os
import random
from tqdm import tqdm

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k"
data_json = f"{base_dir}/alpaca_data_cleaned.json"

dev_f = f"{base_dir}/debug_alpaca_data_cleaned.json"

jd_list = json.load(open(data_json, "r"))

train_jd = json.load(open(data_json))

json.dump(train_jd[:100], fp=open(dev_f, 'w'))
print(f"save to:{dev_f}")
