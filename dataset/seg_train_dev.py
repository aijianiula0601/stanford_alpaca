import json
import random

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/alpace_cot"
data_json = f"{base_dir}/alpaca_cot_merged.json"

train_f = f"{base_dir}/train_alpaca_cot_merged.json"
dev_f = f"{base_dir}/dev_alpaca_cot_merged.json"

jd_list = json.load(open(data_json, "r"))
random.shuffle(jd_list)
dev_num = 1000

train_jd_list = jd_list[:-dev_num]
dev_jd_list = jd_list[-dev_num:]

train_jd = json.load(open(data_json))
json.dump(train_jd_list, fp=open(train_f, 'w'))
json.dump(dev_jd_list, fp=open(dev_f, 'w'))
print(f"train:{len(json.load(open(train_f)))} save to:{train_f}")
print(f"dev:{len(json.load(open(dev_f)))} save to:{dev_f}")
