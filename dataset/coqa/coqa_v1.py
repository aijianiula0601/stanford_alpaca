import os
import sys
import json
from tqdm import tqdm
from joblib import Parallel, delayed
from pathlib import Path

HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"


def get_qa(data_dic={}):
    story = data_dic['story']
    questions = data_dic['questions']
    answers = data_dic['answers']

    cur_dialogues = {BACKGROUND_KEY: story, HUMAN_NAME_KEY: "user", BOT_NAME_KEY: "assistant"}
    qas = []
    for q, a in zip(questions, answers):
        q_input_text = q['input_text']
        a_input_text = a['input_text']

        assert q['turn_id'] == a['turn_id'], f"error turn_id for q-a: {q['turn_id']} != {a['turn_id']}"

        qas.append({f"turn_{a['turn_id']}": {QUESTION_KEY: q_input_text, ANSWER_KEY: a_input_text}})

    cur_dialogues[QAS_KEY] = qas

    return cur_dialogues


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/coqa"
train_f = f"{base_dir}/coqa-train-v1.0.json"
dev_f = f"{base_dir}/coqa-dev-v1.0.json"
org_f_list = [train_f, dev_f]

for org_f in org_f_list:
    f_data = json.load(open(org_f))

    example_list = []
    results = Parallel(n_jobs=16, backend="multiprocessing")(
        delayed(get_qa)(example) for example in tqdm(f_data['data']))
    for res in results:
        example_list.append(res)

    save_f = f"{base_dir}/processed_{Path(org_f).name}"
    print("对话个数：", len(example_list))
    json.dump(example_list, fp=open(save_f, "w", encoding="utf-8"))
    print(f"save to:{save_f}")
    print(f"example:\n{json.dumps(example_list[0])}")
    print("-" * 100)
