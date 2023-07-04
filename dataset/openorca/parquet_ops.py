import os
import sys
import json
import pandas as pd
from pandas import read_parquet

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdf)
print(f"pdf:{pdf}")

from dataset.data_utils import *

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/OpenOrca"

f_name_list = [
    "1M-GPT4-Augmented",
    "3_5M-GPT3_5-Augmented",
]

for f_name in f_name_list:
    org_f = f"{base_dir}/{f_name}.parquet"
    save_f = f"{base_dir}/{f_name}.json"

    data = read_parquet(org_f)
    print(data.count())
    print('-' * 20)
    print(data.head())
    print('-' * 20)

    df_data = read_parquet(org_f, columns=['id', 'system_prompt', 'question', 'response'])

    all_example_list = []

    for index in df_data.index:
        if index % 10000 == 0:
            print(index)
        background = df_data['system_prompt'][index]
        question = df_data['question'][index]
        response = df_data['response'][index]

        example = {
            DATASET_KEY: OPENORCA_DATASET_NAME,
            BACKGROUND_KEY: background,
            HUMAN_NAME_KEY: HUMAN_DEFAULT_NAME,
            BOT_NAME_KEY: BOT_DEFAULT_NAME,
            QAS_KEY: {"turn_0": {QUESTION_KEY: question, ANSWER_KEY: response}}
        }

        all_example_list.append(example)

    print(f"all:{len(all_example_list)}")
    json.dump(all_example_list, open(save_f, 'w'))
    print(f"save to:{save_f}")
    print("-" * 100)
