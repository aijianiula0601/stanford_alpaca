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


def trans_qas2list(example):
    qas_list = []
    turn_n = len(example["qas"].keys())

    for i in range(turn_n):
        qas_list.append(example["qas"][f"turn_{i}"])

    example['qas'] = qas_list

    return example


def insert_data2es(example_list):
    for example in tqdm(example_list):
        ex = trans_qas2list(example)
        insert_example(INDEX_NAME, ex)

    print(f"insert {len(example_list)} to es done!")
    print("-" * 100)


# ---------------------------------------------------------------
# 挑选Alpaca-CoT的一些数据进行训练
# 原链接：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT
# ---------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT"

# -------------------
# alpaca
# -------------------
alpaca_file_list = [f"{base_dir}/alpaca/alpaca_data_cleaned.json"]
insert_data2es(process_f(alpaca_file_list[0]))

# # -------------------
# # alpacaGPT4
# # -------------------
# alpacaGPT4_file_list = [f"{base_dir}/alpacaGPT4/alpaca_gpt4_data.json"]
#
# # -------------------
# # Auto-CoT
# # -------------------
# auto_coT_dir = f"{base_dir}/Auto-CoT"
# auto_coT_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
#
# # -------------------
# # Chain-of-Thought
# # -------------------
#
# chain_of_thought_dir = f"{base_dir}/Chain-of-Thought/formatted_cot_data"
# chain_of_thought_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
#
# # -------------------
# # CodeAlpaca
# # -------------------
# codealpaca_dir = f"{base_dir}/CodeAlpaca"
# codealpaca_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]
#
# # -------------------
# # ConvAI2
# # -------------------
# convAI2_file_list = [f"{base_dir}/ConvAI2/persona_train_self_revised.json"]
#
# # -------------------
# # FLAN-Muffin
# # -------------------
#
# flan_muffin_file_list = [f"{base_dir}/FLAN-Muffin/flan.json"]
#
# # -------------------
# # FastChat
# # -------------------
# fastchat_file_list = [f"{base_dir}/FastChat/Vicuna.json"]
#
# # -------------------
# # GPT4all
# # -------------------
#
# # 不要，这里的数据不是Gpt4的，它是一个GPT for all 的项目收集的数据, https://github.com/nomic-ai/gpt4all
# # 其数据来源，是其他大模型的。不是gpt-4的
# # gpt4all_file_list=[f'{base_dir}/GPT4all/gpt4all_without_p3.json']
#
# # -------------------
# # GPTeacher
# # -------------------
#
# GPTeacher_dir = f"{base_dir}/GPTeacher"
# gpteacher_file_list = [str(f) for f in Path(auto_coT_dir).rglob("*.json")]
#
# # -------------------
# # finance
# # -------------------
#
# finance_file_list = [f"{base_dir}/finance/finance_en.json"]
#
# # -------------------
# # Guanaco
# # -------------------
#
# guanaco_file_list = [f"{base_dir}/Guanaco//Guanaco_additional_Dataset.json"]
#
# # -------------------
# # instinwild
# # -------------------
#
# instinwild_file_list = [
#     f"{base_dir}/instinwild/instinwild_en.json",
#     f"{base_dir}/instinwild/instinwild_ch.json",
# ]
#
# # -------------------
# # instruct
# # -------------------
#
# instruct_file_list = [f'{base_dir}/instruct/instruct.json']
#
# # -------------------
# # prosocial dialog
# # -------------------
#
# prosocial_dialog_file_list = [f"{base_dir}/prosocial-dialog/dialog_safety/train.json"]
#
# # -------------------------------------------
# # xP3
# #   这个数据太大了，应该加载不了那么大的数据集
# # -------------------------------------------
#
# # xP3_file_list = [f"{base_dir}/xP3/en/merged_en.json"]
# # all_f_list.extend(xP3_file_list)
#
# if __name__ == '__main__':
#     save_base_dir = sys.argv[1]
#     all_example_list = []
#     for f in tqdm(all_f_list):
#         example_list = process_f(f)
#         all_example_list.extend(example_list)
#
#     print(f"all_n:{len(all_example_list)}")
#     save_f = f"{save_base_dir}/train_data.json"
#     json.dump(all_example_list, open(save_f, 'w'))
#     print(f"save to:{save_f}")
