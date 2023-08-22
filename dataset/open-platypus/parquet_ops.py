import os
import sys
import json
import pandas as pd
from pandas import read_parquet

# 下载链接：https://huggingface.co/datasets/cnn_dailymail/tree/refs%2Fconvert%2Fparquet/3.0.0

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/Open-Platypus"
org_f = f"{base_dir}/train-00000-of-00001-5b226e5ae97bf4b1.parquet"
save_f = f"{base_dir}/train-00000-of-00001-5b226e5ae97bf4b1_qas.txt"

df_data = read_parquet(org_f, columns=['input', 'output', 'instruction'])

with open(save_f, 'w') as fw:
    for index in df_data.index:
        input_str = df_data['input'][index]
        output_str = df_data['output'][index]
        instruction_str = df_data['instruction'][index]

        example = {
            BACKGROUND_KEY: input_str,
            HUMAN_NAME_KEY: HUMAN_DEFAULT_NAME,
            BOT_NAME_KEY: BOT_DEFAULT_NAME,
            QAS_KEY: {'turn_0': {QUESTION_KEY: instruction_str, ANSWER_KEY: output_str}}
        }
        fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_f}")
