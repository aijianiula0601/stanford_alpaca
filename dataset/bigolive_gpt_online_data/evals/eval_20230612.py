import os

from tqdm import tqdm
import copy

from llama_result import *

# -----------------------------------------------------------------
# gpt线上的数据去调用我们的模型获取答案
# 模型对应关系：
# share_sota_bigolive：
#   /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitype_data/ft_out_sharegpt_soda_bilivechat_mask_head/checkpoint-2400
# multitype_ft2_bigolive：
#   /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/multitype_data_ft2_soda4w_gpt35sex_biglivechat/ft_outs_fix_mask/checkpoint-900
# -----------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/20230613"
gpt_dialogue_json_f = f"test_model_dialogues20230608.json"
# if_self_prompt = True  # 采用自己的prompt
# save_gpt_dialogue_json_f = f"{base_dir}/20230613_eval_data.json"
save_gpt_dialogue_json_f = f"{base_dir}/20230613_eval_data_gpt_prompt.json"  # 采用gpt的prompt
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

            example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="multitype_ft2_bigolive",
                                                             if_self_prompt=if_self_prompt)  # 用mulitype数据训练完，再ft线上数据的模型
            example['qas'][i]['answer-2'] = llama_no_mask_respond(cur_example, if_self_prompt=if_self_prompt,
                                                                  model_name="801")  # 城琦就的tansformer训练的no-mask模型
            example['qas'][i]['answer-3'] = llama_no_mask_respond(cur_example, if_self_prompt=if_self_prompt,
                                                                  model_name="802")  # 城琦新的tansformer训练的no-mask模型
            example['qas'][i]['answer-4'] = my_llama_respond(cur_example, model_name="share_sota_bigolive",
                                                             if_self_prompt=if_self_prompt)  # 直接训练sharegpt、soda、biglive数据的模型

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
