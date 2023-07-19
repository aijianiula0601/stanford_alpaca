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


def insert_data2es(example_list):
    global glob_i
    for example in tqdm(example_list):
        insert_example(INDEX_NAME, trans_qas2list(example), id=glob_i)
        glob_i += 1

    print(f"insert {len(example_list)} to es done!")
    print("-" * 100)
    del example_list


# ---------------------------------------------------------------
# 挑选Alpaca-CoT的一些数据进行训练
# 原链接：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT
# ---------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT"

# -------------------
# alpaca
# -------------------
data_file_list = [f"{base_dir}/alpaca/alpaca_data_cleaned.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# alpacaGPT4
# -------------------
data_file_list = [f"{base_dir}/alpacaGPT4/alpaca_gpt4_data.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# Auto-CoT
# -------------------
auto_coT_dir = f"{base_dir}/Auto-CoT"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# Chain-of-Thought
# -------------------

chain_of_thought_dir = f"{base_dir}/Chain-of-Thought/formatted_cot_data"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# CodeAlpaca
# -------------------
codealpaca_dir = f"{base_dir}/CodeAlpaca"
data_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# ConvAI2
# -------------------
data_file_list = [f"{base_dir}/ConvAI2/persona_train_self_revised.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# FLAN-Muffin
# -------------------

data_file_list = [f"{base_dir}/FLAN-Muffin/flan.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# FastChat
# -------------------
data_file_list = [f"{base_dir}/FastChat/Vicuna.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# GPT4all
# -------------------

# 不要，这里的数据不是Gpt4的，它是一个GPT for all 的项目收集的数据, https://github.com/nomic-ai/gpt4all
# 其数据来源，是其他大模型的。不是gpt-4的
# gpt4all_file_list=[f'{base_dir}/GPT4all/gpt4all_without_p3.json']

# -------------------
# GPTeacher
# -------------------

GPTeacher_dir = f"{base_dir}/GPTeacher"
data_file_list = [str(f) for f in Path(auto_coT_dir).rglob("*.json")]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# finance
# -------------------

data_file_list = [f"{base_dir}/finance/finance_en.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# Guanaco
# -------------------

data_file_list = [f"{base_dir}/Guanaco//Guanaco_additional_Dataset.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# instinwild
# -------------------

data_file_list = [
    f"{base_dir}/instinwild/instinwild_en.json",
    f"{base_dir}/instinwild/instinwild_ch.json",
]
insert_data2es(process_f(data_file_list[0]))

# -------------------
# instruct
# -------------------

data_file_list = [f'{base_dir}/instruct/instruct.json']
insert_data2es(process_f(data_file_list[0]))

# -------------------
# prosocial dialog
# -------------------

data_file_list = [f"{base_dir}/prosocial-dialog/dialog_safety/train.json"]
insert_data2es(process_f(data_file_list[0]))

# -------------------------------------------
# xP3
#   这个数据太大了，应该加载不了那么大的数据集
# -------------------------------------------

data_file_list = [f"{base_dir}/xP3/en/merged_en.json"]
insert_data2es(process_f(data_file_list[0]))
