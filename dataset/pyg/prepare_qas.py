import json
import os
import sys
from tqdm import tqdm
import traceback

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *


def process_conversation(conversation_str):
    try:
        narrative = ""
        qas = []
        qas_flag = False
        for line in conversation_str.split("\n"):
            narrative += line

            if '<START>'.lower() in line.lower():
                qas_flag = True
                continue

            if qas_flag:
                sps = line.split(": ")
                qas.append({"from": sps[0], 'value': ''.join(sps[1:]).strip('"')})

        qas[0]['narrative'] = narrative
        return qas
    except Exception as e:
        print(e)
        return None


base_dir = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/pyg_processed'
org_f = f"{base_dir}/pyg_processed.json"
save_f_qa = f"{base_dir}/pyg_processed_qas.json"
save_f_fv = f"{base_dir}/pyg_processed_fv.json"
org_data_dic = json.load(open(org_f))

# --------------------------
# 处理为from value格式
# --------------------------
form_value_list = []
for k in tqdm(org_data_dic.keys()):
    for conversion in org_data_dic[k]:
        example = process_conversation(conversion)
        if example is not None:
            form_value_list.append(example)

print(f"from value list:{len(form_value_list)}")
json.dump(form_value_list, open(save_f_fv, 'w'))
print(f"save to:{save_f_fv}")

# --------------------------
# 处理为qas格式
# --------------------------
qas_data_list = []
skip_n = 0
dataset_name = PYG_DATASET_NAME
for turns_data in tqdm(form_value_list):
    if len(turns_data) < 2:
        continue
    try:
        background = None
        qas = {}
        human_name = turns_data[0]['from']
        bot_name = turns_data[1]['from']
        turn_i = 0
        for i, td in enumerate(turns_data):
            assert td['value'].strip() != "", "empty value!"

            if i == 0:
                background = td['narrative']
            if (i + 1) % 2 == 1:
                assert human_name == td['from'], f"error human_name"
                qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
            else:
                assert bot_name == td['from'], "error bot_name"
                qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value']
                turn_i += 1

        turn_n = len(qas)
        if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
            qas.pop(f"turn_{turn_n - 1}")

        if len(qas) < 1:
            continue

        assert background is not None
        qas_data_list.append(
            {BACKGROUND_KEY: background,
             DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})
    except Exception as e:
        print(e)
        skip_n += 1

print(f"all_n:{len(qas_data_list)},skip:{skip_n}")
json.dump(qas_data_list, open(save_f_qa, 'w'))
print(f"save to:{save_f_qa}")
