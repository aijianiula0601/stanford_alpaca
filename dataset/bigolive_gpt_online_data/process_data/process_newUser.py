import json
import os
from tqdm import tqdm

from dataset.bigolive_gpt_online_data.process_data.data_ops import *

# ------------------------------------------------------------------------
# 处理新用户打招呼数据
# ------------------------------------------------------------------------


base_dir = "/Users/jiahong/Downloads"

csv_f_list = [
    f"{base_dir}/2023-07-08_robot1.csv",
    f"{base_dir}/2023-07-09_robot1.csv",
    f"{base_dir}/2023-07-10_robot1.csv",
    f"{base_dir}/2023-07-08_robot23.csv",
    f"{base_dir}/2023-07-09_robot23.csv",
    f"{base_dir}/2023-07-10_robot23.csv",
]

save_f = "/Users/jiahong/Downloads/save_test.json"

example_list = []
for csv_f in csv_f_list:
    example_list.extend(read_org_csv_f(csv_f))

json.dump(example_list, open(save_f, 'w'))
print(len(example_list))
print(json.dumps(example_list[:3]))
