import os
import sys
import json
import random
from tqdm import tqdm
import traceback

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

org_f = sys.argv[1]
save_f = sys.argv[2]

other_data = []
bigolive_coloquial_data_list = []

with open(org_f) as fr:
    for line in fr:
        example = json.loads(line)
        if example[DATASET_KEY] == BIGOLIVE_ONLINE_CHAT_DATASET_NAME:
            bigolive_coloquial_data_list.append(example)
        else:
            other_data.append(example)

# 复制多份
other_data = other_data + other_data
all_data = other_data + bigolive_coloquial_data_list

random.shuffle(all_data)

with open(save_f, 'w', buffering=1) as fw:
    for item in all_data:
        fw.write(f"{json.dumps(item)}\n")

print(f"save to:{save_f}")
