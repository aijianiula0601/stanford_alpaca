import json
import os
from tqdm import tqdm

from dataset.bigolive_gpt_online_data.process_data.data_ops import *

# ------------------------------------------------------------------------
# 处理新用户打招呼数据
# ------------------------------------------------------------------------


csv_f = "/Users/jiahong/Downloads/2023-07-11_1700837.csv"

example_list = read_org_csv_f(csv_f)

print(len(example_list))
print(json.dumps(example_list[:3]))
