import json
import requests
import sys
import os
from tqdm import tqdm
import copy
import random

from llama_result import *

# -----------------------------------------------------------------
# gpt线上的数据去调用我们的模型获取答案
# 方案1：
# 服务部署：在v100_f178和f165中
# cd /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval
# python -m http.server 8085
# 方案2：
# 打开https://jsongrid.com/这个网站，把内容复制过去
# -----------------------------------------------------------------

limit_dialogue_n = 20
limit_turn_n = 20

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval"
gpt_dialogue_json_f = f"{base_dir}/2023-06-07_1527353_dilogue.json"
save_gpt_dialogue_json_f = f"{base_dir}/20230609_eval_data.json"

gpt_dialogue_json_data = json.load(open(gpt_dialogue_json_f))

all_keys = list(gpt_dialogue_json_data.keys())

random.shuffle(all_keys)

all_keys = all_keys[:limit_dialogue_n]

new_dialogue_data_dic = {}
d_i = 0
for k in tqdm(all_keys):
    error_flag = False
    example = gpt_dialogue_json_data[k]
    example['qas'] = example['qas'][:limit_turn_n]
    try:
        turn_n = len(example['qas'])
        for i in range(turn_n):
            cur_example = copy.deepcopy(example)
            cur_example['qas'] = cur_example['qas'][:i + 1]
            del cur_example['qas'][-1]['answer']

            example['qas'][i]['no_mask_answer'] = llama_no_mask_respond(cur_example)
            example['qas'][i]['gpt35sex_answer'] = my_llama_respond(cur_example, model_name="gpt35sex")
            example['qas'][i]['gpt35sex_v1_answer'] = my_llama_respond(cur_example, model_name="gpt35sex_self_prompt")
            example['qas'][i]['mask_head_answer'] = my_llama_respond(cur_example, model_name="mask_head_answer")


    except Exception as e:
        print(e)
        error_flag = True
    if error_flag:
        continue
    else:
        new_dialogue_data_dic[f"dialogue-{d_i}"] = example
        d_i += 1

json.dump(new_dialogue_data_dic, open(save_gpt_dialogue_json_f, 'w'))
print(f"save to:{save_gpt_dialogue_json_f}")
