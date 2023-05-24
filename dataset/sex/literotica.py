import os
import sys
import json
import jsonlines
import random
from tqdm import tqdm

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/text/sex/Literotica.jsonl"
sample_10w_f = "/mnt/cephfs/hjh/common_dataset/nlp/text/sex/Literotica_sammple_10w.json"
debug_sample_10w_f = "/mnt/cephfs/hjh/common_dataset/nlp/text/sex/debug_Literotica_sammple_100.json"
all_data = []

with open(org_f, "r+", encoding="utf8") as f:
    for item in tqdm(jsonlines.Reader(f)):
        all_data.append(item["text"])

print(f"all:{len(all_data)}")
random_select_10w_data = random.sample(all_data, 100000)

json.dump(random_select_10w_data, open(sample_10w_f, 'w'))
json.dump(random_select_10w_data[:100], open(debug_sample_10w_f, 'w'))
print(f"sample:{len(random_select_10w_data)}")
print(f"save to:{sample_10w_f}")
