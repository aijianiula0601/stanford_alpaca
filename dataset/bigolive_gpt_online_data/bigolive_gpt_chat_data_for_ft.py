import json
from tqdm import tqdm
import csv

# -----------------------------------------------------------------
# 获取bigolive线上的数据进行整理
# -----------------------------------------------------------------


json_f = "/Users/jiahong/Downloads/2023-06-07_1528241_dilogue.json"
save_json_f = "/Users/jiahong/Downloads/2023-06-07_1528241_dilogue_data.json"
save_debug_json_f = "/Users/jiahong/Downloads/debug_2023-06-07_1528241_dilogue_data.json"

json_data = json.load(open(json_f))

new_data_list = []
for k in json_data.keys():
    example = json_data[k]
    new_data_list.append(example)

json.dump(new_data_list, open(save_json_f, "w"))
json.dump(new_data_list[:100], open(save_debug_json_f, "w"))
print(f"save to:{save_json_f}")
print(f"save to:{save_debug_json_f}")
