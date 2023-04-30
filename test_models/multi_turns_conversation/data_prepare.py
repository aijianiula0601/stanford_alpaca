import os
import json

HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"

# ------------------------------------------------------------
# stanford_52k
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/train_alpaca_data_cleaned.json"
stanford_52k_data = []
for d in json.load(open(org_f)):
    human_name = "Instruction"
    bot_name = "Response"
    background = d['input']

    stanford_52k_data.append(
        {BACKGROUND_KEY: background,
         HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: {
             "turn_0": {QUESTION_KEY: d['instruction'] + f"\n\n### Input:\n{background}", ANSWER_KEY: d["output"]}}
         })

# print(json.dumps(stanford_52k))

# ------------------------------------------------------------
# soda
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
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

    assert background is not None
    soda_data.append({BACKGROUND_KEY: background, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name, QAS_KEY: qas})

# print(json.dumps(soda_data))

# ------------------------------------------------------------
# gpt4
# ------------------------------------------------------------

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun/gpt4_shared_data.json"
gpt4_data = []

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

        gpt4_data.append({BACKGROUND_KEY: background, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name, QAS_KEY: qas})
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
for example in json.load(open(org_f)):
    background = example['profile_information']
    human_name = "human"
    bot_name = "Ai"
    cur_qas = {}
    for i, qa in enumerate(example['qas']):
        cur_qas[f"turn_{i}"] = {QUESTION_KEY: qa['question'], ANSWER_KEY: qa['answer']}

    persona_chat_data.append(
        {BACKGROUND_KEY: background, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name, QAS_KEY: cur_qas})

# print(json.dumps(persona_chat_data))

# ------------------------------------------------------------
# empathetic_dialogues
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues/train.json"
empathetic_dialogues_data = []

for example in json.load(open(org_f)):
    background = ''
    human_name = "human"
    bot_name = "Ai"
    cur_qas = {}
    for i, qa in enumerate(example['qas']):
        cur_qas[f"turn_{i}"] = {QUESTION_KEY: qa['question'], ANSWER_KEY: qa['answer']}

    empathetic_dialogues_data.append(
        {BACKGROUND_KEY: background, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name, QAS_KEY: cur_qas})

# print(json.dumps(empathetic_dialogues_data))

# ============================================================
# 汇总所有数据
# ============================================================

save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun_conversation/multi_dataset_qas.json"

data = {"soda": soda_data,
        "gpt4": gpt4_data,
        "persona_chat": persona_chat_data,
        "empathetic_dialogues": empathetic_dialogues_data,
        "stanford_52k": stanford_52k_data
        }

json.dump(data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
