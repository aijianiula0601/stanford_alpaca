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


def process_f(org_f, columns=['prompt', 'response'], if_check=True):
    data = pq.read_table(org_f, columns=columns)

    all_dialogue_data = []
    for i, row in data.to_pandas().iterrows():
        line = row[columns[0]].strip() + " " + row[columns[1]]
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

    if if_check:
        print(f"checking file:{org_f}")
        all_example = 0
        skip_example = 0
        new_all_dialogue_data = []
        for qas in all_dialogue_data:
            all_example += 1
            flag = True
            for item in qas:
                if item[VALUE_KEY].replace("\n", "").strip() == "":
                    flag = False
                    skip_example += 1
                    break
            if flag:
                new_all_dialogue_data.append(qas)
        print(f"checked done! org examples:{all_example},skip examples:{skip_example}")
        all_dialogue_data = new_all_dialogue_data

    return all_dialogue_data


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rm/rm-static"

test_f = f"{base_dir}/test-00000-of-00001-8c7c51afc6d45980.parquet"
train_f = f"{base_dir}/train-00000-of-00001-2a1df75c6bce91ab.parquet"

rm_static_train_data = process_f(train_f)

# test_data = process_f(test_f)
# random.shuffle(test_data)
# print(json.dumps(test_data))

# ------------------------------------------------------------
# full-hh-rlhf
# ------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rl/full-hh-rlhf"

test_f = f"{base_dir}/test-00000-of-00001-ec71e9262143a91c.parquet"
train_f = f"{base_dir}/train-00000-of-00001-8349d0765e6718df.parquet"

full_hh_rlhf_train_data = process_f(train_f)
# print(json.dumps(full_hh_rlhf_train_data))

# ------------------------------------------------------------
# synthetic-instruct-gptj-pairwise
# ------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rm/synthetic-instruct-gptj-pairwise"
org_f = f"{base_dir}/train-00000-of-00001-1e5d57b93c448e7a.parquet"

synthetic_instruct_gptj_pairwise_data = []
data = pq.read_table(org_f, columns=['prompt', 'chosen'])
for i, row in data.to_pandas().iterrows():
    synthetic_instruct_gptj_pairwise_data.append(
        [{FROM_KEY: HUMAN_NAME, VALUE_KEY: row['prompt']}, {FROM_KEY: ASSISTANT_NAME, VALUE_KEY: row['chosen']}])
# print(json.dumps(synthetic_instruct_gptj_pairwise_data))

# ------------------------------------------------------------
# yitingxie/rlhf-reward-datasets
# ------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rl/rlhf-reward-datasets"
train_f = f"{base_dir}/train-00000-of-00001-2ea3039ca4da89f8.parquet"
rlhf_reward_datasets_data = process_f(train_f, columns=['prompt', 'chosen'])
# print(json.dumps(rlhf_reward_datasets_data))

# ------------------------------------------------------------
# combine all
# ------------------------------------------------------------
base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multi_turns_conversation_nomask"
save_f = f"{base_dir}/add_deepspeedchat_example_dataset/train.json"
deepspeedchat_example_dataset_data = rm_static_train_data + full_hh_rlhf_train_data + synthetic_instruct_gptj_pairwise_data + rlhf_reward_datasets_data

org_multi_turns_f = f"{base_dir}/multi_dataset_qas.json"

org_multi_turns_data = json.load(open(org_multi_turns_f))

all_data = deepspeedchat_example_dataset_data + org_multi_turns_data
random.shuffle(all_data)

print(f"examples:{len(all_data)}")
json.dump(all_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
