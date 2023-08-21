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
# OpenOrca中的gpt4数据
# ------------------------------------------------------------
data_base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/OpenOrca"
f_p = f"{data_base_dir}/1M-GPT4-Augmented_qas_refined_0810.json"
openorca_data_list = json.load(open(f_p))
random.shuffle(openorca_data_list)
openorca_data_list = openorca_data_list[:50000]
dataset_name = OPENORCA_DATASET_NAME
for example in openorca_data_list:
    example[DATASET_KEY] = dataset_name
    example[MASK_HEAD_KEY] = True
    example[MASK_QUESTION_KEY] = True
    example[MASK_EXCEPT_LAST_ANSWER] = False

print(f"dataset:{dataset_name},all_n:{len(openorca_data_list)}")

# ------------------------------------------------------------
# 加载口语化的bigolive turns数据
# ------------------------------------------------------------

bigolive_colloquial_f = sys.argv[1]

bigolive_coloquial_data_list = []
with open(bigolive_colloquial_f) as fr:
    for line in tqdm(fr.readlines()):
        example = json.loads(line)
        example[DATASET_KEY] = BIGOLIVE_ONLINE_CHAT_DATASET_NAME
        example[MASK_HEAD_KEY] = True
        example[MASK_QUESTION_KEY] = True
        example[MASK_EXCEPT_LAST_ANSWER] = False
        example[MASK_EXCEPT_LAST_QUESTION_ANSWER] = False
        bigolive_coloquial_data_list.append(example)

print(f"dataset:{BIGOLIVE_ONLINE_CHAT_DATASET_NAME},all_n:{len(bigolive_coloquial_data_list)}")

# ------------------------------------------------------------
# OllieStanley/oa_dolly_15k
# 阅读理解类型
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/databricks-dolly-15k/prepare2qas_databricks-dolly-15k.json"
dataset_name = DATABRICKS_DOLLY_15K_DATASET_NAME

databricks_dolly_15k_data_list = json.load(open(org_f))
random.shuffle(databricks_dolly_15k_data_list)
databricks_dolly_15k_data_list = databricks_dolly_15k_data_list[:50000]
for example in databricks_dolly_15k_data_list:
    example[DATASET_KEY] = dataset_name
    example[MASK_HEAD_KEY] = True
    example[MASK_QUESTION_KEY] = True
    example[MASK_EXCEPT_LAST_ANSWER] = False

print(f"dataset:{dataset_name},all_n:{len(databricks_dolly_15k_data_list)}")

# ------------------------------------------------------------
# cnn_dailymail
# 总结类型
# ------------------------------------------------------------

# 这里有11w数据
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00000-of-00003.json"
dataset_name = CNN_DAILYMAIL_DATASET_NAME

cnn_dailymail2qas_data_list = json.load(open(org_f))
random.shuffle(cnn_dailymail2qas_data_list)
cnn_dailymail2qas_data_list = cnn_dailymail2qas_data_list[:50000]
new_cnn_dailymail2qas_data_list = []
for example in cnn_dailymail2qas_data_list:
    if len(example[BACKGROUND_KEY]) > 2500:
        continue
    example[DATASET_KEY] = dataset_name
    example[MASK_HEAD_KEY] = True
    example[MASK_QUESTION_KEY] = True
    example[MASK_EXCEPT_LAST_ANSWER] = False
    new_cnn_dailymail2qas_data_list.append(example)

cnn_dailymail2qas_data_list = new_cnn_dailymail2qas_data_list
print(f"dataset:{dataset_name},all_n:{len(cnn_dailymail2qas_data_list)}")

# ------------------------------------------------------------
# soda
# 这个数据之前犯了个错误，之前训练时候mask question，纠正为只mask head
# ------------------------------------------------------------
org_f = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_cleaned.json'
soda_data_list = json.load(open(org_f))
random.shuffle(soda_data_list)
soda_data_list = soda_data_list[:50000]
print(f"dataset name:soda, all_n:{len(soda_data_list)}")

# ------------------------------------------------------------
# persona_chat
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/personaChat/prepared_personality_qas.json"
persona_chat_data = json.load(open(org_f))
random.shuffle(persona_chat_data)
persona_chat_data = persona_chat_data[:50000]
dataset_name = PERSONA_CHAT_DATASET_NAME
print(f"dataset:{dataset_name},all_n:{len(persona_chat_data)}")

# ------------------------------------------------------------
# gpt_roleplay_realm
# 角色扮演对话
# 有个216个角色，每个角色有20个对话
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/gpt_roleplay_realm/en-00000-of-00001-6291ef0dc79c47ed_qas.json"
dataset_name = GPT_ROLEPLAY_DATASET_NAME

gpt_roleplay_realm_data_list = json.load(open(org_f))
random.shuffle(gpt_roleplay_realm_data_list)
gpt_roleplay_realm_data_list = gpt_roleplay_realm_data_list[:50000]

background_example_dic = {}

for example in gpt_roleplay_realm_data_list:
    example[DATASET_KEY] = dataset_name
    background = example[BACKGROUND_KEY]
    if background not in background_example_dic:
        background_example_dic[background] = [example]
    else:
        background_example_dic[background].append(example)
    # 不要在这里设置mask了，清洗数据时候已经加好的，因为有user和人设各自发起对话的情况

# 每个角色随机选择两个对话就好
gpt_roleplay_realm_data_list = []
for k in background_example_dic:
    gpt_roleplay_realm_data_list.extend(random.sample(background_example_dic[k], k=2))

print(f"dataset:{dataset_name},all_n:{len(gpt_roleplay_realm_data_list)}")


# ------------------------------------------------------------
# empathetic_dialogues
# 这里的数据有情感类别在，感觉加入训练的作用不大，因为跟类别相关，而且有时候第一个问题跟人设描述一样
# ------------------------------------------------------------

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


save_f = sys.argv[2]

other_data = soda_data_list + persona_chat_data + databricks_dolly_15k_data_list + cnn_dailymail2qas_data_list + openorca_data_list + gpt_roleplay_realm_data_list

random.shuffle(other_data)

random.shuffle(bigolive_coloquial_data_list)
data = other_data + bigolive_coloquial_data_list[:5000]

random.shuffle(data)


with open(save_f,'w',buffering=1) as fw:
    user_ask_first_n = 0
    all_n = 0
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
