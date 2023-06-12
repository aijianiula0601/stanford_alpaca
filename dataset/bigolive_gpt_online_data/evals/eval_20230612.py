import os

from tqdm import tqdm
import copy

from llama_result import *

# -----------------------------------------------------------------
# gpt线上的数据去调用我们的模型获取答案
# -----------------------------------------------------------------

limit_dialogue_n = 20
limit_turn_n = 20

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/20230613"
gpt_dialogue_json_f = f"test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/20230613_eval_data.json"

os.system(f"mkdir -p {base_dir}")

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

            example['qas'][i]['answer-1'] = my_llama_respond(cur_example, model_name="multitype_ft2_bigolive",
                                                             if_self_prompt=True)
            example['qas'][i]['answer-2'] = llama_no_mask_respond(cur_example, if_self_prompt=True, model_name="801")
            example['qas'][i]['answer-3'] = llama_no_mask_respond(cur_example, if_self_prompt=True, model_name="802")
            example['qas'][i]['answer-4'] = my_llama_respond(cur_example, model_name="share_sota_bigolive",
                                                             if_self_prompt=True)

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
