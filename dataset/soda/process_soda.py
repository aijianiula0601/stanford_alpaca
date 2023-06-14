import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitype_data"
os.system(f"mkdir -p {save_base_dir}")

# ------------------------------------------------------------
# sota
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
dataset_name = SOTA_DATASET_NAME

skip_empty_qa_n = 0
soda_data = []
for turns_data in tqdm(json.load(open(org_f))):
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

    skip_qa = False
    for i in range(len(qas)):
        qa = qas[f"turn_{i}"]
        question = qa[QUESTION_KEY].strip()
        answer = qa[ANSWER_KEY].strip()
        if question == "" or answer == "":
            skip_empty_qa_n += 1
            skip_qa = True
            break

    if skip_qa:
        continue

    assert background is not None
    soda_data.append(
        {BACKGROUND_KEY: background,
         DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
         QAS_KEY: qas})

print(f"dataset name:{dataset_name},all_n:{len(soda_data)}, skip_empty_qa_n:{skip_empty_qa_n}")

save_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"

json.dump(soda_data, open(save_f, 'w'))
print(f"save to:{save_f}")
