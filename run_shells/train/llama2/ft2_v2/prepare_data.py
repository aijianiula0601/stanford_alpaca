import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

org_data_file = sys.argv[1]
org_data_list = json.load(open(org_data_file))


def filter_qa(qas: dict):
    """过滤"""
    filter_flag = False
    filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model",
                        "reason=, msg = {}",
                        "text-based program"]

    qas_l = len(qas)
    new_qas = {}
    for ti in range(qas_l):
        qa = qas[f"turn_{ti}"]
        for fw in filter_word_list:
            if fw.lower() in qa[QUESTION_KEY].lower() or fw.lower() in qa[ANSWER_KEY].lower():
                filter_flag = True
                break
        if filter_flag:
            break

        if "what's your name".lower() in qa[QUESTION_KEY].lower():
            if "What's yours".lower() in qa[ANSWER_KEY].lower() or "What's your name".lower() in qa[
                ANSWER_KEY].lower() or "What about you".lower() in qa[ANSWER_KEY].lower():
                break

        if "what's your name".lower() in qa[ANSWER_KEY].lower() and ti < qas_l - 1:
            next_turn_qa = qas[f"turn_{ti + 1}"]
            if "What's yours".lower() in next_turn_qa[ANSWER_KEY].lower() or "What's your name".lower() in \
                    next_turn_qa[
                        ANSWER_KEY].lower() or "What about you".lower() in next_turn_qa[ANSWER_KEY].lower():
                break

        new_qas[f"turn_{ti}"] = qa

    if len(new_qas) > 0:
        return new_qas
    else:
        return None


# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[2]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

random.shuffle(org_data_list)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in org_data_list:
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
            user_ask_first_n += 1
    except Exception as e:
        user_ask_first_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")

json.dump(checked_data[:200], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
