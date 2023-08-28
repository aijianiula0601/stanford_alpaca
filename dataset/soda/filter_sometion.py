import os
import sys
import json
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *
from dataset.filter_ops import *

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda"

f = f"{base_dir}/soda_train_name_qas.json"
save_f = f"{base_dir}/soda_train_name_qas_cleaned.txt"

# ---------------------------
# 过滤
# 1. 前后的 \ /
# 2. 长度大于220回答的
# 由于这个数据有可能是人设先问问题，所以只mask head, question也要过滤。
# ---------------------------


data_list = json.load(open(f))

new_data_list = []
all_n = 0
skip_n = 0
for example in tqdm(data_list):
    all_n += 1

    # ---- 过滤较段人设 ----
    if len(example['background']) <= 250:  # 人设太短不利于模型逻辑训练
        skip_n += 1
        continue

    qas = example['qas']
    new_qas = {}
    for i in range(len(qas)):
        qa = qas[f'turn_{i}']
        # ---- 清洗qa ----
        qa['question'] = qa['question'].strip().strip("/").strip("\\")
        qa['answer'] = qa['answer'].strip().strip("/").strip("\\")
        qa['question'] = clear_qa(qa['question'])
        qa['answer'] = clear_qa(qa['answer'])
        # ---- 过滤较长qa ----
        if check_qa(qa['question']) or check_qa(qa['answer']):
            break
        # ---- 过滤较长qa ----

        new_qas[f'turn_{i}'] = qa

    example['qas'] = new_qas
    if len(new_qas) > 0:
        new_data_list.append(example)
    else:
        skip_n += 1

print(f"all:{all_n},skip:{skip_n}, now:{len(new_data_list)}")

with open(save_f, 'w') as fw:
    for example in new_data_list:
        fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_f}")
