import os
import sys
import json
import random
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

f_p = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/pyg_processed/pyg_processed_qas.json'
f_data_list = json.load(open(f_p))

# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

random.shuffle(f_data_list)

checked_data = []

user_ask_first_n = 0
all_n = 0
for item in f_data_list:
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
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{user_ask_first_n},all_n:{all_n}")

json.dump(checked_data[:500], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
