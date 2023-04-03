import json
from pathlib import Path
from tqdm import tqdm

# ---------------------------------------------------------------------------------
# 合并Alpace-CoT项目的所有文件，下载其github项目，在其目录的data/formatted_cot_data下。
# git 地址：https://github.com/PhoebusSi/Alpaca-CoT
# json文件：
# aqua_train.json
# creak_train.json
# ecqa_train.json
# esnli_train.json
# gsm8k_train.json
# qasc_train.json
# qed_train.json
# sensemaking_train.json
# strategyqa_train.json
# ---------------------------------------------------------------------------------


json_dir = "/Users/jiahong/PycharmProjects/nlp/Alpaca-CoT/data/formatted_cot_data"

merger_json_f = "/Users/jiahong/Downloads/alpaca_cot_merged.json"

js_data_list = []
for js_f in tqdm([str(f) for f in Path(json_dir).glob("*.json")]):
    cur_json_data = json.load(open(js_f, "r"))
    print(f"len:{len(cur_json_data)}, file:{js_f}")
    js_data_list += cur_json_data

print(f"共有数据:{len(js_data_list)}")

json.dump(js_data_list, fp=open(merger_json_f, "w"))

print(f"save to:{merger_json_f}")
