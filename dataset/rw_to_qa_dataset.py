import json
import re
import sys
import random
from pandas import read_parquet
import pyarrow.parquet as pq

# ------------------------------------------------------------
# 把deepspeedExample中的数据集处理为qa格式
# ------------------------------------------------------------


# ------------------------------------------------------------
# Dahoas/rm-static
# url:https://huggingface.co/datasets/Dahoas/rm-static
# ------------------------------------------------------------
HUMAN_NAME = "Human"
ASSISTANT_NAME = "Assistant"
FROM_KEY = "from"
VALUE_KEY = "value"


def process_f(org_f: str):
    data = pq.read_table(org_f, columns=['prompt', 'response'])

    all_dialogue_data = []
    for i, row in data.to_pandas().iterrows():
        line = row['prompt'].strip() + " " + row['response']
        cleaned_line = []
        for d in line.split("\n"):
            if d.strip("\n").strip() == "":
                continue
            cleaned_line.append(d)

        cur_qas_split_list = re.split('(Human:|Assistant:)', '\n'.join(cleaned_line).strip())[1:]
        assert len(cur_qas_split_list) % 2 == 0, f"error qa line:{cur_qas_split_list}"

        cur_qas_list = []
        for qa_group in [cur_qas_split_list[i:i + 2] for i in range(0, len(cur_qas_split_list), 2)]:
            if qa_group[0] == HUMAN_NAME + ":":
                cur_qas_list.append({FROM_KEY: HUMAN_NAME, VALUE_KEY: qa_group[1].strip()})
            elif qa_group[0] == ASSISTANT_NAME + ":":
                cur_qas_list.append({FROM_KEY: ASSISTANT_NAME, VALUE_KEY: qa_group[1].strip()})
            else:
                raise Exception(f"Error qa:{cur_qas_split_list}")

        assert len(cur_qas_split_list) % 2 == 0, f"Error cur_qa_list:{cur_qas_list}"
        all_dialogue_data.append(cur_qas_list)

    return all_dialogue_data


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rm"

test_f = f"{base_dir}/test-00000-of-00001-8c7c51afc6d45980.parquet"
train_f = f"{base_dir}/train-00000-of-00001-2a1df75c6bce91ab.parquet"

rm_static_train_data = process_f(train_f)
random.shuffle(rm_static_train_data)
print("-----:", len(rm_static_train_data))

test_data = process_f(train_f)
random.shuffle(test_data)
print(json.dumps(test_data))

# ------------------------------------------------------------
# full-hh-rlhf
# ------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rl/full-hh-rlhf"

test_f = f"{base_dir}/test-00000-of-00001-ec71e9262143a91c.parquet"
train_f = f"{base_dir}/train-00000-of-00001-8349d0765e6718df.parquet"

full_hh_rlhf_train_data = process_f(train_f)
random.shuffle(full_hh_rlhf_train_data)
print(json.dumps(full_hh_rlhf_train_data))

# ------------------------------------------------------------
#
# ------------------------------------------------------------
