import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitype_data"
os.system(f"mkdir -p {save_base_dir}")

# ------------------------------------------------------------
# sota
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
dataset_name = SODA_DATASET_NAME

soda_data = []
for turns_data in json.load(open(org_f)):
    background = None
    qas = {}
    human_name = turns_data[0]['from']
    bot_name = turns_data[1]['from']
    turn_i = 0
    for i, td in enumerate(turns_data):
        if i == 0:
            background = td['narrative']
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

    assert background is not None
    soda_data.append(
        {BACKGROUND_KEY: background,
         DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: qas})

print(f"dataset name:{dataset_name},all_n:{len(soda_data)}")

# 在俊士数据基础上清理出来
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt/cleaned_gpt4_shared_data.json"
shared_gpt_data = []
dataset_name = SHAREGPT_DATASET_NAME

user_ask_first_n = 0
all_n = 0
for turns_data in json.load(open(org_f)):
    all_n += 1
    if len(turns_data) <= 1:
        user_ask_first_n += 1
        continue
    background = ''
    qas = {}
    try:
        # human_name = HUMAN_DEFAULT_NAME
        # bot_name = BOT_DEFAULT_NAME
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

print(f"dataset_name:{dataset_name},skip_n:", user_ask_first_n, "all_n:", all_n)

# ============================================================
# bigolive线上聊天数据
# ============================================================

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230607_qas.json"

bigolive_chat_data_list = json.load(open(org_f))
dataset_name = BIGOLIVE_ONLINE_CHAT_DATASET_NAME

for example in tqdm(bigolive_chat_data_list):
    example[DATASET_KEY] = dataset_name

print(f"---datasetname:{BIGOLIVE_ONLINE_CHAT_DATASET_NAME},all_n:{len(bigolive_chat_data_list)}")

# ============================================================
# 汇总所有数据
# ============================================================

save_f = f"{save_base_dir}/sharegpt_soda_bilivechat_dataset_qas.json"
debug_save_f = f"{save_base_dir}/debug_sharegpt_soda_bilivechat_dataset_qas.json"

data = soda_data + \
       shared_gpt_data + \
       bigolive_chat_data_list
random.shuffle(data)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in data:
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
        user_ask_first_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")

json.dump(checked_data[:500], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
