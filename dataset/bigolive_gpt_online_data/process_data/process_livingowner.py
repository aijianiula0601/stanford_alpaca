import json
import os
import sys
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)

from dataset.bigolive_gpt_online_data.process_data.data_ops import *

# ------------------------------------------------------------------------
# 处理主播数据
# ------------------------------------------------------------------------


base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/v2"
csv_f = f"{base_dir}/20230601~0710_livingowner.csv"

save_f = f"{base_dir}/20230601~0710_livingowner_qas.json"

example_list = []
example_list.extend(read_org_csv_f_livingowner(csv_f))

json.dump(example_list, open(save_f, 'w'))
print("all_n:", len(example_list))
print(f"save to:{save_f}")
