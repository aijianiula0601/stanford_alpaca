import os
import json
import random
from tqdm import tqdm

HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"

# ------------------------------------------------------------
# stanford_52k
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/train_alpaca_data_cleaned.json"
dataset_name = "stanford_52k"

stanford_52k_data = []
for d in json.load(open(org_f)):
    human_name = "Instruction"
    bot_name = "Response"
    background = d['input']

    stanford_52k_data.append(
        {BACKGROUND_KEY: background,
         HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         DATASET_KEY: dataset_name,
         QAS_KEY: {
             "turn_0": {QUESTION_KEY: d['instruction'] + f"\n\n### Input:\n{background}", ANSWER_KEY: d["output"]}}
         })

# print(json.dumps(stanford_52k))

# ------------------------------------------------------------
# sota
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
dataset_name = "sota"

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

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun/gpt4_shared_data.json"
gpt4_data = []
dataset_name = "gpt4"

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

        gpt4_data.append(
            {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})
    except Exception as e:
        # print(e, f"data:{json.dumps(turns_data)}")
        # print("-" * 100)
        pass

# print("skip_n:", skip_n, "all_n:", all_n)
# print(json.dumps(gpt4_data))

# ------------------------------------------------------------
# persona_chat
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/train.json"
persona_chat_data = []
dataset_name = "gpt4"
for example in json.load(open(org_f)):
    background = example['profile_information']
    human_name = "human"
    bot_name = "Ai"
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
dataset_name = "empathetic_dialogues"

for example in json.load(open(org_f)):
    background = ''
    human_name = "human"
    bot_name = "Ai"
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

save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun_conversation/multi_dataset_qas.json"
debug_save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun_conversation/debug_multi_dataset_qas.json"

data = soda_data + gpt4_data + persona_chat_data + empathetic_dialogues_data + stanford_52k_data
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
