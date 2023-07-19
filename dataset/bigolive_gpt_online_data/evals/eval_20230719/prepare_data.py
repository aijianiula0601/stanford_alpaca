import os
import sys
from tqdm import tqdm
import copy

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

from llama_result import *

time_day = "20230719"
base_dir = f"/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/{time_day}"
gpt_dialogue_json_f = f"{pdj}/test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/{time_day}_eval_data.json"
# if_self_prompt = True  # 采用自己的prompt
if_self_prompt = False  # 采用gpt原始的prommpt

os.system(f"mkdir -p {base_dir}")

gpt_dialogue_json_data = json.load(open(gpt_dialogue_json_f))

all_keys = list(gpt_dialogue_json_data.keys())

new_dialogue_data_dic = {}
d_i = 0
for k in tqdm(all_keys):
    error_flag = False
    example = gpt_dialogue_json_data[k]
    example['qas'] = example['qas']
    try:
        turn_n = len(example['qas'])
        for i in range(turn_n):
            cur_example = copy.deepcopy(example)
            cur_example['qas'] = cur_example['qas'][:i + 1]
            del cur_example['qas'][-1]['answer']

            # --------------------------------
            # vicuna-7b直接ft multitype数据
            # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v7/ft_out/checkpoint-12000
            # --------------------------------
            example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v7",
                                                             if_self_prompt=if_self_prompt)
            # --------------------------------
            # vicuna-7bft multitype+cot数据
            # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v10/ft_out/checkpoint-10940
            # --------------------------------
            example['qas'][i]['answer-2'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v10",
                                                             if_self_prompt=if_self_prompt)


    except Exception as e:
        print("-" * 100)
        print(f"error:{e}")
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
