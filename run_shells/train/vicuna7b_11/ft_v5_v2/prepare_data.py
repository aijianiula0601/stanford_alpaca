import os
import sys
import json
import random
from pathlib import Path
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

auto_cot_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/auto-cot/qas"
chain_fo_thought_dir = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Chain-of-Thought/formatted_cot_data/qas"

multitype_data_p = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v5/train_data.json"

# -------auto_cot-------
auto_cot_data_list = []
for f in Path(auto_cot_dir).glob("*.json"):
    auto_cot_data_list.extend(json.load(open(f)))
print(f"auto_cot_n:{len(auto_cot_data_list)}")

# -------chain_fo_thought-------
chain_fo_thought_data_list = []
for f in Path(auto_cot_dir).glob("*.json"):
    chain_fo_thought_data_list.extend(json.load(open(f)))
print(f"chain_fo_thought_n:{len(chain_fo_thought_data_list)}")

# -------mulititype_data-------
multitype_data_list = json.load(open(multitype_data_p))
print(f"multitype_data_n:{len(multitype_data_list)}")

# ============================================================
# 汇总所有数据
# ============================================================


save_base_dir = sys.argv[1]
save_f = f"{save_base_dir}/train_data.json"
debug_save_f = f"{save_base_dir}/debug_data.json"

data = multitype_data_list + auto_cot_data_list + chain_fo_thought_data_list

checked_data = []

skip_n = 0
all_n = 0
for item in data:
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
        skip_n += 1
        print(e, f"item:{json.dumps(item)}")

json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")
print(f"skip:{skip_n},all_n:{all_n}")

json.dump(checked_data[:500], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
