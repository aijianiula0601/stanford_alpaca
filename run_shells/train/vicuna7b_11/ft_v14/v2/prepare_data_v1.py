import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

v3_train_data_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v14/v3/train_data.json"
v3_train_data_list = json.load(open(v3_train_data_f))

# ------------------------------------------------------------
# bigolive数据，大约3.6w，暂时不需要bigolive数据，爬其效果影响
# ------------------------------------------------------------
f_p = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4/v5/train_data_cleaned.json'
bigolive_data_list = json.load(open(f_p))[:3000]
dataset_name = BIGOLIVE_ONLINE_CHAT_DATASET_NAME
for example in bigolive_data_list:
    example[DATASET_KEY] = dataset_name
    example[MASK_HEAD_KEY] = True
    example[MASK_QUESTION_KEY] = True
    example[MASK_EXCEPT_LAST_ANSWER] = False


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


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"

data_list = v3_train_data_list + bigolive_data_list
random.shuffle(data_list)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in data_list:
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
            checked_data.append(item)
        else:
            user_ask_first_n += 1
    except Exception as e:
        user_ask_first_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")
