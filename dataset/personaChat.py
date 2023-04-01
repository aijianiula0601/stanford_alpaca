import pandas as pd
import csv
from pathlib import Path
import json
import os

PROMPT_DICT = {
    "background_chat": (
        "Let's play a role-playing dialogue. Here is your profile information:\n"
        "{background}\n"
        "Here is a conversation between {role_a} and {role_b}\n"
        "{history}"
    ),
    "no_background_chat": (
        "Here is a conversation between {role_a} and {role_b}, do not generate multiple rounds of reply.\n"
        "{history}"
    )
}

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
            # if j % 2 == 0:
            #     print(f"Human:", qa_l)
            # else:
            #     print(f"   AI:", qa_l)
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

os.system(f"rm -rf {save_f}")
json.dump(personaChat_list, fp=open(save_f, 'w', encoding='utf-8'))
# print(f"save to:{save_f}")

jd = json.load(open(save_f, "r"))
print(json.dumps(jd[1]))

# ---------------------------------
# 命令执行：
# python personaChat.py|jq .
# ---------------------------------
