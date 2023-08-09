import os
import sys
import json
import random
from tqdm import tqdm
import traceback

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/v2"
f1_p = f"{base_dir}/20230708-20230710_robot123_qas.json"
f2_p = f"{base_dir}/20230601~0710_livingowner_qas.json"

f1_data_list = json.load(open(f1_p))
f2_data_list = json.load(open(f2_p))

# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

random.shuffle(f1_data_list)
data = f1_data_list + f2_data_list
random.shuffle(data)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in tqdm(data):
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
        user_ask_first_n += 1
        traceback.print_exc(e)
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")

json.dump(checked_data[:500], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
