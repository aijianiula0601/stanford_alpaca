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


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/empathetic_dialogues"
data_f = f"{base_dir}/prepared_train.json"

train_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues/train.json"
debug_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues/debug.json"

jd_list = json.load(open(data_f, "r"))

train_jd = []
one_qas_list = []
multi_qas_list = []

for jd in tqdm(jd_list):
    len_qas = len(jd['qas'])
    if len_qas == 1:
        one_qas_list.append(jd)
    elif len_qas > 1:
        multi_qas_list.append(jd)

print(f"只有一个对话的数量:{len(one_qas_list)}")
print(f"多轮对话的数量:{len(multi_qas_list)}")

for i in tqdm(range(0, 3)):
    print(f"turn:{i}")
    for jd in tqdm(multi_qas_list):
        len_qas = len(jd['qas'])
        jd["qas"] = jd['qas'][:random.randint(1, len_qas)]
        train_jd.append(jd)

train_jd += one_qas_list
print(f"len:{len(train_jd)}")
json.dump(train_jd, fp=open(train_f, 'w'))
print(f"save to:{train_f}")

json.dump(train_jd[:100], fp=open(debug_f, 'w'))
print(f"save to:{debug_f}")
