import os
import sys
import json
import random
from tqdm import tqdm
import traceback

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

# ------------------------------------------------------------
# 为了跟v2做对比实验，加载v2中除了bigolive的数据
# ------------------------------------------------------------


org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v2/train_data.json"
org_data_list = json.load(open(org_f))
filter_bigolive_other_data_list = []
all_n = 0
skip_n = 0
for example in org_data_list:
    all_n += 1
    if example[DATASET_KEY] == BIGOLIVE_ONLINE_CHAT_DATASET_NAME or example[DATASET_KEY] == BIGOLIVE_CHAT_ROBOT:
        skip_n += 1
        continue
    else:
        filter_bigolive_other_data_list.append(example)

print(f"all_n:{all_n},filter bigolive:{skip_n}, other_dataset:{len(filter_bigolive_other_data_list)}")

# ------------------------------------------------------------
# bigolive数据，大约3.6w，暂时不需要bigolive数据，爬其效果影响
# ------------------------------------------------------------
f_p = sys.argv[1]
bigolive_data_list = open(f_p).readlines()
dataset_name = BIGOLIVE_ONLINE_CHAT_DATASET_NAME
new_bigolive_data_list = []
for example_line in bigolive_data_list:
    example = json.loads(example_line)
    example[DATASET_KEY] = dataset_name
    example[MASK_HEAD_KEY] = True
    example[MASK_QUESTION_KEY] = True
    example[MASK_EXCEPT_LAST_ANSWER] = False
    new_bigolive_data_list.append(example)

print(f"dataset:{dataset_name},all_n:{len(bigolive_data_list)}")


def filter_qa(qas: dict):
    """过滤"""
    filter_flag = False
    filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model",
                        "reason=, msg = {}",
                        "text-based program", "As shown in figure"]
    new_qas = {}
    for turn_i in qas:
        qa = qas[turn_i]
        for fw in filter_word_list:
            if fw.lower() in qa[QUESTION_KEY].lower() or fw.lower() in qa[ANSWER_KEY].lower():
                filter_flag = True
                break
        if filter_flag:
            break

        new_qas[turn_i] = qa

    if len(new_qas) > 0:
        return new_qas
    else:
        return None


# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[2]
save_f = f"{save_base_dir}/train_data.txt"

data = filter_bigolive_other_data_list + new_bigolive_data_list
random.shuffle(data)

user_ask_first_n = 0
all_n = 0

with open(save_f, 'w', buffering=1) as fw:
    for item in data:
        all_n += 1
        try:
            assert BACKGROUND_KEY in item
            assert HUMAN_NAME_KEY in item
            assert BOT_NAME_KEY in item
            assert QAS_KEY in item
            assert MASK_HEAD_KEY in item
            assert MASK_QUESTION_KEY in item
            assert MASK_EXCEPT_LAST_ANSWER in item
            for turn_i in item[QAS_KEY]:
                assert QUESTION_KEY in item[QAS_KEY][turn_i]
                assert ANSWER_KEY in item[QAS_KEY][turn_i]

            new_qas = filter_qa(item[QAS_KEY])
            if new_qas is not None:
                item[QAS_KEY] = new_qas
                fw.write(f"{json.dumps(item)}\n")
            else:
                user_ask_first_n += 1
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            user_ask_first_n += 1
            print(e, f"item:{json.dumps(item)}")

print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")
