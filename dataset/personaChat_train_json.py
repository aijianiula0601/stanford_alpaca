import pandas as pd
import csv
from pathlib import Path
import json
import os
import random
from tqdm import tqdm

# ----------------------------------------------------------------------------------------------------------------
# 先执行：personaChat_test.py
# 随机获取qas的历史记录，生成训练数据≥
# ----------------------------------------------------------------------------------------------------------------


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/personaChat"
data_f = f"{base_dir}/personality.csv"

save_f = f"{base_dir}/prepared_personality.json"
train_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/my_prepared_personality.json"
dev_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/prepared_debug_personality.json"

jd_list = json.load(open(save_f, "r"))

train_jd = []

for i in tqdm(range(0, 20)):
    print(f"turn:{i}")
    for jd in tqdm(jd_list):
        len_qas = len(jd['qas'])
        cut_qa_jd = {"profile_information": jd['profile_information'], "qas": jd['qas'][:random.randint(1, len_qas)]}
        train_jd.append(cut_qa_jd)

print(f"len:{len(train_jd)}")
json.dump(train_jd, fp=open(train_f, 'w'))
print(f"save to:{train_f}")

json.dump(train_jd[:100], fp=open(dev_f, 'w'))
print(f"save to:{dev_f}")
