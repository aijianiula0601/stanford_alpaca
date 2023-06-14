import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

# 在俊士数据基础上清理出来
base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt"
org_f = f"{base_dir}/cleaned_gpt4_shared_data.json"
save_f = f"{base_dir}/cleaned_gpt4_shared_data_qas.json"
shared_gpt_data = []
dataset_name = SHAREGPT_DATASET_NAME

skip_n = 0
all_n = 0
skip_empty_qa_n = 0
for turns_data in json.load(open(org_f)):
    all_n += 1
    if len(turns_data) <= 1:
        skip_n += 1
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

        skip_qa = False
        for i in range(len(qas)):
            qa = qas[f"turn_{i}"]
            question = qa[QUESTION_KEY].strip()
            answer = qa[ANSWER_KEY].strip()
            if question == "" or answer == "":
                skip_empty_qa_n += 1
                skip_qa = True
                skip_n += 1
                break
        if skip_qa:
            continue

        shared_gpt_data.append(
            {BACKGROUND_KEY: background, DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})
    except Exception as e:
        print(e, f"data:{json.dumps(turns_data)}")
        print("-" * 100)
        pass

print(f"dataset_name:{dataset_name},skip_n:", skip_n, "skip_empty_qa_n:", skip_empty_qa_n, "all_n:", all_n)

json.dump(shared_gpt_data, open(save_f, 'w'))
print(f"save to:{save_f}")
