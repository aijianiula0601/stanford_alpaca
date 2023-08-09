import csv
import json
import os
import sys

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

# ----------------------------------------------------------------------------------------------------------------
# 保存到文件的数据格式是：[
# {"profile_information":"",[
#                               {"question": "", "answer": "", "turn_i":0}
#                           ],..}
# ...]
# 其中：profile_information以第一人称来描述机器人的角色，question 人类提问的、answer是机器人回答的
# ----------------------------------------------------------------------------------------------------------------


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/personaChat"
data_f = f"{base_dir}/personality.csv"

save_f = f"{base_dir}/prepared_personality.json"
save_qas_f = f"{base_dir}/prepared_personality_qas.json"

personaChat_list = []

i = 0
ini_i = 100
with open(data_f, encoding='utf-8-sig') as f:
    for row in csv.reader(f, skipinitialspace=True):
        if i < 1:
            i += 1
            continue
        i += 1
        persona = row[1]  # 以第一人称来描述机器人的角色
        qas = row[2]

        qa_list = []
        turn_i = 0
        question = None
        for j, qa_l in enumerate(qas.strip("\n").split("\n")):
            if j % 2 == 0:
                question = qa_l
            elif j % 2 == 1:
                qa_dic = {"question": question, "answer": qa_l, "turn_i": turn_i}  # question 人类提问的、answer是机器人回答的
                qa_list.append(qa_dic)
                turn_i += 1
            else:
                raise Exception("Error!")

        assert len(qa_list) > 0, f"error qa list,org row:{row}"

        personaChat_list.append({"profile_information": persona, "qas": qa_list})
f.close()

json.dump(personaChat_list, fp=open(save_f, 'w'))
print(f"对话组数：{len(personaChat_list)}")  # 8939
print(f"save to:{save_f}")

# ---------------------------------
# 转换为qas格式的数据
# ---------------------------------

persona_chat_qas_data = []
dataset_name = PERSONA_CHAT_DATASET_NAME
for example in tqdm(personaChat_list):
    background = example['profile_information']
    human_name = HUMAN_DEFAULT_NAME
    bot_name = BOT_DEFAULT_NAME
    cur_qas = {}
    for i, qa in enumerate(example['qas']):
        cur_qas[f"turn_{i}"] = {QUESTION_KEY: qa['question'], ANSWER_KEY: qa['answer']}

    persona_chat_qas_data.append(
        {
            BACKGROUND_KEY: background,
            MASK_HEAD_KEY: True,
            MASK_QUESTION_KEY: True,
            MASK_EXCEPT_LAST_ANSWER: False,
            DATASET_KEY: dataset_name,
            HUMAN_NAME_KEY: human_name,
            BOT_NAME_KEY: bot_name,
            QAS_KEY: cur_qas
        })

json.dump(persona_chat_qas_data, fp=open(save_qas_f, 'w'))
print(f"对话组数：{len(persona_chat_qas_data)}")  # 8939
print(f"save to:{save_qas_f}")
