import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data"

# ------------------------------------------------------------
# alpaca_gpt4
# instruction input类型
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/alpaca_gpt4/prepare2qas_alpaca_gpt4_data_unfiltered.json"
dataset_name = ALPACA_GPT4

alpaca_gpt4_data_list = json.load(open(org_f))

for example in alpaca_gpt4_data_list:
    example[DATASET_KEY] = dataset_name

# print(json.dumps(alpaca_gpt4_data))

# ------------------------------------------------------------
# unnatural_instruction_gpt4
# instruction input类型
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/unnatural_instruction_gpt4/prepare2qas_unnatural_instructions_unfiltered_data.json"
dataset_name = UNNATURAL_INSTRUCTION_DATASET_NAME
unnatural_instruction_gpt4_data_list = json.load(open(org_f))

for example in unnatural_instruction_gpt4_data_list:
    example[DATASET_KEY] = dataset_name

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
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
dataset_name = SOTA_DATASET_NAME

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

# print(json.dumps(soda_data))

# ------------------------------------------------------------
# gpt4
# ------------------------------------------------------------

# org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun/gpt4_shared_data.json"
# gpt4_shared_data = []
# dataset_name = SHAREGPT_DATASET_NAME
#
# skip_n = 0
# all_n = 0
# for turns_data in json.load(open(org_f)):
#     all_n += 1
#     if len(turns_data) <= 1:
#         skip_n += 1
#         continue
#     background = ''
#     qas = {}
#     try:
#         human_name = turns_data[0]['from']
#         bot_name = turns_data[1]['from']
#         turn_i = 0
#         for i, td in enumerate(turns_data):
#             if (i + 1) % 2 == 1:
#                 assert human_name == td['from']
#                 qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
#             else:
#                 assert bot_name == td['from']
#                 qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value']
#                 turn_i += 1
#
#         turn_n = len(qas)
#         if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
#             qas.pop(f"turn_{turn_n - 1}")
#
#         if len(qas) < 1:
#             continue
#
#         gpt4_shared_data.append(
#             {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
#              QAS_KEY: qas})
#     except Exception as e:
#         # print(e, f"data:{json.dumps(turns_data)}")
#         # print("-" * 100)
#         pass
#
# # print("skip_n:", skip_n, "all_n:", all_n)
# # print(json.dumps(gpt4_data))

# ------------------------------------------------------------
# persona_chat
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/train.json"
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

save_f = f"{save_base_dir}/multi_dataset_qas.json"
debug_save_f = f"{save_base_dir}/debug_multi_dataset_qas.json"

data = soda_data + persona_chat_data + empathetic_dialogues_data + alpaca_gpt4_data_list + unnatural_instruction_gpt4_data_list + databricks_dolly_15k_data_list + cnn_dailymail2qas_data_list
random.shuffle(data)

checked_data = []

skip_n = 0
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
        skip_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{skip_n},all_n:{all_n}")

json.dump(checked_data[:100], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
