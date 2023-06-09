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
# -----------------------------------------------------------------

limit_dialogue_n = 20
limit_turn_n = 15

base_dir = "/Users/jiahong/Downloads"
gpt_dialogue_json_f = "test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/20230609_eval.json"

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
