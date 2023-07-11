import os

from tqdm import tqdm
import copy

from llama_result import *

# -----------------------------------------------------------------
# 我们训练的mulitype_data跟程琦的模型做对比
# 模型对应关系：
# llama_multitype_data：
#   /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft_outs_fix_id2/checkpoint-4000
# vicuna-7b_ft_v5：
#   /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v5/ft_out/checkpoint-4000
# 对比结果：vicuna-7b_ft_v5 > llama_multitype_data > 802
# -----------------------------------------------------------------

date_time_str = "20230628"

base_dir = f"/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/{date_time_str}"

# 直接采用上一次测试的数据调用的802结果
eval_20230612_json_f = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/20230613/20230613_eval_data.json'

if_self_prompt = True  # 采用自己的prompt
save_gpt_dialogue_json_f = f"{base_dir}/{date_time_str}_eval_data.json"
# save_gpt_dialogue_json_f = f"{base_dir}/{date_time_str}_eval_data_gpt_prompt.json"  # 采用gpt的prompt
# if_self_prompt = False  # 采用gpt原始的prommpt

os.system(f"mkdir -p {base_dir}")

eval_20230612_json_data = json.load(open(eval_20230612_json_f))

all_keys = list(eval_20230612_json_data.keys())

new_dialogue_data_dic = {}
d_i = 0
for k in tqdm(all_keys):
    error_flag = False
    example = eval_20230612_json_data[k]
    example['qas'] = example['qas']
    try:
        turn_n = len(example['qas'])
        for i in range(turn_n):
            cur_example = copy.deepcopy(example)
            cur_example['qas'] = cur_example['qas'][:i + 1]
            del cur_example['qas'][-1]['answer']

            example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="llama_multitype_data",
                                                             if_self_prompt=if_self_prompt)
            example['qas'][i]['answer-2'] = example['qas'][i]['answer-3']  # answer-3是之前802的结果
            example['qas'][i]['answer-3'] = my_llama_respond(cur_example, model_name="vicuna-7b_ft_v5",
                                                             if_self_prompt=if_self_prompt)

            del example['qas'][i]['answer-4']


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
