import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

# ------------------------------------------------------------
# bigolive数据，只拿4w
# ------------------------------------------------------------


f_p = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4/cleaned_v2_train_data.json'
bigolive_data_list = json.load(open(f_p))[:40000]

# ------------------------------------------------------------
# databricks-dolly-15k
# 阅读理解类型
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/databricks-dolly-15k/prepare2qas_databricks-dolly-15k.json"
dataset_name = DATABRICKS_DOLLY_15K_DATASET_NAME

databricks_dolly_15k_data_list = json.load(open(org_f))
for example in databricks_dolly_15k_data_list:
    example[DATASET_KEY] = dataset_name

# ------------------------------------------------------------
# cnn_dailymail2qas.py
# 总结类型
# ------------------------------------------------------------

# 这里有11w数据
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00000-of-00003.json"
dataset_name = CNN_DAILYMAIL_DATASET_NAME

limit_n = 50000
cnn_dailymail2qas_data_list = json.load(open(org_f))
random.shuffle(cnn_dailymail2qas_data_list)
for example in cnn_dailymail2qas_data_list[:limit_n]:
    example[DATASET_KEY] = dataset_name

# ------------------------------------------------------------
# sota
# ------------------------------------------------------------
org_f = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_filter_sometion.json'

soda_data_list = json.load(open(org_f))
print(f"dataset name:soda, all_n:{len(soda_data_list)}")

# print(json.dumps(soda_data))

# ------------------------------------------------------------
# persona_chat
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/prepared_train_personality.json"
persona_chat_data = []
dataset_name = PERSONA_CHAT_DATASET_NAME
for example in json.load(open(org_f)):
    background = example['profile_information']
    human_name = HUMAN_DEFAULT_NAME
    bot_name = BOT_DEFAULT_NAME
    cur_qas = {}
    for i, qa in enumerate(example['qas']):
        cur_qas[f"turn_{i}"] = {QUESTION_KEY: qa['question'], ANSWER_KEY: qa['answer']}

    persona_chat_data.append(
        {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: cur_qas})

# print(json.dumps(persona_chat_data))

# ------------------------------------------------------------
# empathetic_dialogues
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues/train.json"
empathetic_dialogues_data = []
dataset_name = EMPATHETIC_DIALOGUES_DATASET_NAME

post_background_text = "Here is a conversation with {emotion_category} for {human_name} and {bot_name} \n\n"

for example in json.load(open(org_f)):
    human_name = HUMAN_DEFAULT_NAME
    bot_name = BOT_DEFAULT_NAME
    background = example['prompt'] + post_background_text.format_map(
        {"emotion_category": example['context'], 'human_name': human_name, 'bot_name': {bot_name}})
    cur_qas = {}
    for i, qa in enumerate(example['qas']):
        cur_qas[f"turn_{i}"] = {QUESTION_KEY: qa['question'], ANSWER_KEY: qa['answer']}

    empathetic_dialogues_data.append(
        {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: cur_qas})

# print(json.dumps(empathetic_dialogues_data))

# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

data = soda_data_list + persona_chat_data + empathetic_dialogues_data + bigolive_data_list + databricks_dolly_15k_data_list + cnn_dailymail2qas_data_list
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
