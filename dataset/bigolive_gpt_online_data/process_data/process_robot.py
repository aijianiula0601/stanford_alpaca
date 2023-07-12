import json
import os
import sys
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)

from dataset.bigolive_gpt_online_data.process_data.data_ops import *

# ------------------------------------------------------------------------
# 处理新用户打招呼数据
# ------------------------------------------------------------------------


base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/v2"

csv_f_list = [
    f"{base_dir}/2023-07-08_robot1.csv",
    f"{base_dir}/2023-07-09_robot1.csv",
    f"{base_dir}/2023-07-10_robot1.csv",
    f"{base_dir}/2023-07-08_robot23.csv",
    f"{base_dir}/2023-07-09_robot23.csv",
    f"{base_dir}/2023-07-10_robot23.csv",
]

save_f = f"{base_dir}/20230708-20230710_robot123_qas.json"

example_list = []
for csv_f in csv_f_list:
    example_list.extend(read_org_csv_f(csv_f))

json.dump(example_list, open(save_f, 'w'))
print("all_n:", len(example_list))

print(f"save to:{save_f}")
