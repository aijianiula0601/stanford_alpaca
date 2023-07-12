from tqdm import tqdm
import copy
import traceback
import os
from llama_result import *

# -----------------------------------------------------------------
# 评估vicuna-7b训练multitype数据和vicuna_7b训练完OpenOrca的模型
# OpenOrca是为了提高prompt理解能力
# vicuna-7b-multitype：/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v5/ft_out/checkpoint-7000
# vicuna-7b-openorca：/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v7/ft_out/checkpoint-11000
# 对应评估中的需求七
# -----------------------------------------------------------------

limit_dialogue_n = 20
limit_turn_n = 10

time_day = "20230711"
base_dir = f"/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/{time_day}"
os.system(f"mkdir -p {base_dir}")
gpt_dialogue_json_f = f"test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/vicuna_7b_multitype_vc_openorca.json"

gpt_dialogue_json_data = json.load(open(gpt_dialogue_json_f))

all_keys = list(gpt_dialogue_json_data.keys())
# random.shuffle(all_keys)

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

            example['qas'][i]['vicuna-7b-multitype'] = my_llama_respond(cur_example,
                                                                        model_name="vicuna-7b_ft_v5",
                                                                        if_self_prompt=False)
            example['qas'][i]['vicuna-7b-openorca'] = my_llama_respond(cur_example,
                                                                       model_name="vicuna-7b_ft_v7",
                                                                       if_self_prompt=False)



    except Exception as e:
        print("-" * 100)
        print(f"error:{e}")
        print(f"dialogue:{example}")
        print("-" * 100)
        error_flag = True
        traceback.print_exc(e)
    if error_flag:
        continue
    else:
        new_dialogue_data_dic[f"dialogue-{d_i}"] = example
        d_i += 1

json.dump(new_dialogue_data_dic, open(save_gpt_dialogue_json_f, 'w'))
print(f"save to:{save_gpt_dialogue_json_f}")
