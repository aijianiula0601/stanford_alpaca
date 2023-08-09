import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

org_data_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v13/v1/train_data.json"
old_train_data_list = json.load(open(org_data_f))

# ----------------------------------------------
# soda采用gpt35改为更加口语化的数据
# ----------------------------------------------

soda_colloquial_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_filter_sometion_to_colloquial.txt"
dataset_name = SOTA_ANGLICIZA_DATASET_NAME
soda_colloquial_data_list = []
with open(soda_colloquial_f, 'r') as fr:
    for line in fr:
        example = json.loads(line.replace("\n", ""))
        example[DATASET_KEY] = dataset_name
        soda_colloquial_data_list.append(example)

print(f"soda_colloquial_data:{len(soda_colloquial_data_list)}")
assert len(soda_colloquial_data_list) > 0


def filter_qa(qas: dict):
    """过滤"""
    filter_flag = False
    filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model",
                        "reason=, msg = {}",
                        "text-based program"]
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


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

data_list = old_train_data_list + soda_colloquial_data_list

random.shuffle(data_list)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in data_list:
    all_n += 1
    try:
        assert BACKGROUND_KEY in item
        assert HUMAN_NAME_KEY in item
        assert BOT_NAME_KEY in item
        assert QAS_KEY in item
        for turn_i in item[QAS_KEY]:
            assert QUESTION_KEY in item[QAS_KEY][turn_i]
            assert ANSWER_KEY in item[QAS_KEY][turn_i]

        new_qas = filter_qa(item[QAS_KEY])
        if new_qas is not None:
            item[QAS_KEY] = new_qas
            checked_data.append(item)
        else:
            user_ask_first_n += 1
    except Exception as e:
        user_ask_first_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")

json.dump(checked_data[:200], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
