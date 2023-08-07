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

# ------------------------------------------------------------
# OpenOrca中的gpt4数据
# ------------------------------------------------------------


data_base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/OpenOrca"
f_p = f"{data_base_dir}/1M-GPT4-Augmented_qas.json"
openorca_data_list = json.load(open(f_p))
random.shuffle(openorca_data_list)
openorca_data_list = openorca_data_list[:40000]

# ------------------------------------------------------------
# bigolive数据，大约3.6w
# ------------------------------------------------------------
f_p = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4/v5/train_data_cleaned.json'
bigolive_data_list = json.load(open(f_p))
random.shuffle(bigolive_data_list)
bigolive_data_list = bigolive_data_list[:10000]

# ------------------------------------------------------------
# OllieStanley/oa_dolly_15k
# 阅读理解类型
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/databricks-dolly-15k/prepare2qas_databricks-dolly-15k.json"
dataset_name = DATABRICKS_DOLLY_15K_DATASET_NAME

databricks_dolly_15k_data_list = json.load(open(org_f))
for example in databricks_dolly_15k_data_list:
    example[DATASET_KEY] = dataset_name

random.shuffle(databricks_dolly_15k_data_list)
databricks_dolly_15k_data_list = databricks_dolly_15k_data_list[:10000]

# ------------------------------------------------------------
# cnn_dailymail
# 总结类型
# ------------------------------------------------------------

# 这里有11w数据
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00000-of-00003.json"
dataset_name = CNN_DAILYMAIL_DATASET_NAME

limit_n = 50000
cnn_dailymail2qas_data_list = json.load(open(org_f))
random.shuffle(cnn_dailymail2qas_data_list)
cnn_dailymail2qas_data_list = cnn_dailymail2qas_data_list[:limit_n]
for example in cnn_dailymail2qas_data_list:
    example[DATASET_KEY] = dataset_name

random.shuffle(cnn_dailymail2qas_data_list)
cnn_dailymail2qas_data_list = cnn_dailymail2qas_data_list[:10000]

print(f"dataset:{dataset_name},all_n:{len(cnn_dailymail2qas_data_list)}")

# ------------------------------------------------------------
# sota
# ------------------------------------------------------------
org_f = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_filter_sometion.json'
soda_data_list = json.load(open(org_f))
print(f"dataset name:soda, all_n:{len(soda_data_list)}")
soda_data_list = soda_data_list[:10000]

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

random.shuffle(persona_chat_data)
persona_chat_data = persona_chat_data[:10000]
print(f"dataset:{dataset_name},all_n:{len(persona_chat_data)}")

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

random.shuffle(empathetic_dialogues_data)
empathetic_dialogues_data = empathetic_dialogues_data[:10000]
print(f"dataset:{dataset_name},all_n:{len(empathetic_dialogues_data)}")


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

data = soda_data_list + persona_chat_data + empathetic_dialogues_data + bigolive_data_list + databricks_dolly_15k_data_list + cnn_dailymail2qas_data_list + openorca_data_list
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

        new_qas = filter_qa(item[QAS_KEY])
        if new_qas is not None:
            item[QAS_KEY] = new_qas
            checked_data.append(item)
        else:
            skip_n += 1
    except Exception as e:
        skip_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{skip_n},all_n:{all_n}")

json.dump(checked_data[:200], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
