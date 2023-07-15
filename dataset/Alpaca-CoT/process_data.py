import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------
# 挑选Alpaca-CoT的一些数据进行训练
# 原链接：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT/tree/main
# ---------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT"



# -------------------
# alpaca
# -------------------
alpaca_file_list = [f"{base_dir}/alpaca/alpaca_data_cleaned.json"]

# -------------------
# alpacaGPT4
# -------------------
alpacaGPT4_file_list = [f"{base_dir}/alpacaGPT4/alpaca_gpt4_data.json"]



# -------------------
# Auto-CoT
# -------------------
auto_coT_dir = f"{base_dir}/Auto-CoT"
auto_coT_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]

# -------------------
# Chain-of-Thought
# -------------------

chain_of_thought_dir = f"{base_dir}/Chain-of-Thought/formatted_cot_data"
chain_of_thought_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]

# -------------------
# CodeAlpaca
# -------------------
codealpaca_dir = f"{base_dir}/CodeAlpaca"
codealpaca_file_list = [str(f) for f in Path(auto_coT_dir).glob("*.json")]

# -------------------
# ConvAI2
# -------------------
convAI2_file_list = [f"{base_dir}/ConvAI2/persona_train_self_revised.json"]

# -------------------
# FLAN-Muffin
# -------------------

flan_muffin_file_list = [f"{base_dir}/FLAN-Muffin/flan.json"]

# -------------------
# FastChat
# -------------------
fastchat_file_list = [f"{base_dir}/FastChat/Vicuna.json"]

# -------------------
# GPT4all
# -------------------

# 不要，这里的数据不是Gpt4的，它是一个GPT for all 的项目收集的数据, https://github.com/nomic-ai/gpt4all
# 其数据来源，是其他大模型的。不是gpt-4的
# gpt4all_file_list=[f'{base_dir}/GPT4all/gpt4all_without_p3.json']

# -------------------
# GPTeacher
# -------------------

GPTeacher_dir=f"{base_dir}/GPTeacher"
gpteacher_file_list = [str(f) for f in Path(auto_coT_dir).rglob("*.json")]


# -------------------
# finance
# -------------------

finance_file_list = [f"{base_dir}/finance/finance_en.json"]


# -------------------
# ConvAI2
# -------------------




# -------------------
# ConvAI2
# -------------------

# -------------------
# ConvAI2
# -------------------


# -------------------
# ConvAI2
# -------------------
