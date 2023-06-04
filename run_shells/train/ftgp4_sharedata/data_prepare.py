import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_gpt4share_data"

os.system(f"mkdir -p {save_base_dir}")

# ------------------------------------------------------------
# alpaca_gpt4
# instruction input类型
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/alpaca_gpt4/prepare2qas_alpaca_gpt4_data_unfiltered.json"
dataset_name = ALPACA_GPT4

alpaca_gpt4_data_list = json.load(open(org_f))

for example in alpaca_gpt4_data_list:
    example[DATASET_KEY] = dataset_name

print(f"---alpaca_gpt4_data_list:{len(alpaca_gpt4_data_list)}")

# ------------------------------------------------------------
# unnatural_instruction_gpt4
# instruction input类型
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/unnatural_instruction_gpt4/prepare2qas_unnatural_instructions_unfiltered_data.json"
dataset_name = UNNATURAL_INSTRUCTION_DATASET_NAME
unnatural_instruction_gpt4_data_list = json.load(open(org_f))

for example in unnatural_instruction_gpt4_data_list:
    example[DATASET_KEY] = dataset_name

print(f"---unnatural_instruction_gpt4_data_list:{len(unnatural_instruction_gpt4_data_list)}")

# ------------------------------------------------------------
# gpt4
# ------------------------------------------------------------

# org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun/gpt4_shared_data.json"
# 在俊士数据基础上清理出来
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt/cleaned_gpt4_shared_data.json"
shared_gpt_data = []
dataset_name = SHAREGPT_DATASET_NAME

skip_n = 0
all_n = 0
for turns_data in json.load(open(org_f)):
    all_n += 1
    if len(turns_data) <= 1:
        skip_n += 1
        continue
    background = ''
    qas = {}
    try:
        human_name = turns_data[0]['from']
        bot_name = turns_data[1]['from']
        turn_i = 0
        for i, td in enumerate(turns_data):
            if (i + 1) % 2 == 1:
                assert human_name == td['from']
                qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
            else:
                assert bot_name == td['from']
                qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value']
                turn_i += 1

        turn_n = len(qas)
        if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
            qas.pop(f"turn_{turn_n - 1}")

        if len(qas) < 1:
            continue

        shared_gpt_data.append(
            {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})
    except Exception as e:
        print(e, f"data:{json.dumps(turns_data)}")
        print("-" * 100)
        pass

print("---shared_gpt_data skip_n:", len(shared_gpt_data))

# ============================================================
# 汇总所有数据
# ============================================================

print("-" * 100)
save_f = f"{save_base_dir}/gpt_data.json"
debug_save_f = f"{save_base_dir}/debug_gpt_data.json"

all_data_list = alpaca_gpt4_data_list + unnatural_instruction_gpt4_data_list + shared_gpt_data
random.shuffle(all_data_list)
print(f"all_data_list:{len(all_data_list)}")

checked_data = []

skip_n = 0
all_n = 0
for item in all_data_list:
    all_n += 1
    try:
        assert BACKGROUND_KEY in item
        assert HUMAN_NAME_KEY in item
        assert BOT_NAME_KEY in item
        assert QAS_KEY in item
        for turn_i in item[QAS_KEY]:
            assert QUESTION_KEY in item[QAS_KEY][turn_i]
            assert ANSWER_KEY in item[QAS_KEY][turn_i]
        checked_data.append(item)
    except Exception as e:
        skip_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{skip_n},all_n:{all_n}")

json.dump(checked_data[:500], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
