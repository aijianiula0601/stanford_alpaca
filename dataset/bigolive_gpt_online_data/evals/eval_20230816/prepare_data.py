import os
import sys
import json
from tqdm import tqdm
import traceback
import copy

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

from llama_result import *

time_day = "20230816"
base_dir = f"/Users/jiahong/Downloads/{time_day}"
gpt_dialogue_json_f = "test_data.txt"
save_gpt_dialogue_json_f = f"{base_dir}/{time_day}_eval_data.json"
# if_self_prompt = True  # 采用自己的prompt
if_self_prompt = False  # 采用gpt原始的prommpt

os.system(f"mkdir -p {base_dir}")


def process_example(example: dict):
    prompt = example['prompt']
    human_name = example['human_name']
    bot_name = example['bot_name']
    new_qas = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        del qa['history']
        new_qas.append(qa)

    return {"prompt": prompt, "human_name": human_name, "bot_name": bot_name, "qas": new_qas}


new_dialogue_data_dic = {}
d_i = 0
with open(gpt_dialogue_json_f) as fr:
    for line in fr:
        example = process_example(json.loads(line))
        error_flag = False
        example['qas'] = example['qas']
        try:
            turn_n = len(example['qas'])
            for i in range(turn_n):
                cur_example = copy.deepcopy(example)
                cur_example['qas'] = cur_example['qas'][:i + 1]
                del cur_example['qas'][-1]['answer']

                # --------------------------------
                # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v3_v2/ft_out/checkpoint-452
                # --------------------------------
                example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v15_v3_v2")


        except Exception as e:
            print("-" * 100)
            traceback.print_exc(e)
            print(f"dialogue:{example}")
            print("-" * 100)
            error_flag = True
        if error_flag:
            continue
        else:
            new_dialogue_data_dic[f"dialogue-{d_i}"] = example
            d_i += 1

json.dump(new_dialogue_data_dic, open(save_gpt_dialogue_json_f, 'w'))
print(f"save to:{save_gpt_dialogue_json_f}")
