import json
import os
import sys
from pathlib import Path
from tqdm import tqdm

pfd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pfd)

from dataset.alpaca_cot.instruction2qas import process_f
from run_shells.train.vicuna7b_11.ft_v12.data_server.insert_es_data import *

INDEX_NAME = "qas_data"

glob_i = 0


def trans_qas2list(example):
    qas_list = []
    turn_n = len(example["qas"].keys())

    for i in range(turn_n):
        qas_list.append(example["qas"][f"turn_{i}"])

    example['qas'] = qas_list

    return example


def get_insert_example(example):
    global glob_i
    idx_ex = {"index": {"_index": INDEX_NAME, "_type": "_doc", "_id": glob_i}}
    ex = trans_qas2list(example)
    glob_i += 1
    return idx_ex, ex


def write2json(example_list, save_f):
    with open(save_f, 'w', buffering=1) as fw:
        for example in tqdm(example_list):
            idx_ex, ex = get_insert_example(example)
            fw.write(f"{idx_ex}\n{ex}\n")

    print(f"save to:{save_f}")


# ---------------------------------------------------------------
# 挑选Alpaca-CoT的一些数据进行训练
# 原链接：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT
# ---------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT"

# -------------------
# alpaca
# -------------------
data_file_list = [f"{base_dir}/alpaca/alpaca_data_cleaned.json"]
save_f = "/tmp/test.json"
write2json(process_f(data_file_list[0]), save_f)
