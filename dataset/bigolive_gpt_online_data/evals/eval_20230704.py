import os

from tqdm import tqdm
import copy

from llama_result import *

# -----------------------------------------------------------------
# 获取数据交给评估人员评估，评估模型有三个：
# vicuna-7b_ft_v4：vicuna-7b直接ft线上数据
# vicuna-7b_ft_v6：vicuna-7bft多种数据后再ft线上数据
# llama_multitype_data_ft2_v4：llama7b ft多种数据后再ft线上数据
# -----------------------------------------------------------------


time_day = "20230704"
base_dir = f"/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/{time_day}"
gpt_dialogue_json_f = f"test_model_dialogues20230608.json"
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
            # vicuna-7b直接ft线上数据
            # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4/ft_out/checkpoint-1200
            # --------------------------------
            example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v4",
                                                             if_self_prompt=if_self_prompt)
            # --------------------------------
            # vicuna-7bft多种数据后再ft线上数据
            # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v6/ft_out/checkpoint-1200
            # --------------------------------
            example['qas'][i]['answer-2'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v6",
                                                             if_self_prompt=if_self_prompt)
            # --------------------------------
            # llama7b ft多种数据后再ft线上数据
            # 模型:/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_v4/ft_outs/checkpoint-1200
            # --------------------------------
            example['qas'][i]['answer-3'] = my_llama_respond(cur_example, model_name="llama_multitype_data_ft2_v4",
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
