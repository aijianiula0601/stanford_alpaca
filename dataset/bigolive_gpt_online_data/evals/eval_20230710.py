from tqdm import tqdm
import copy
import traceback
from dataset.bigolive_gpt_online_data.evals.llama_result import *

# -----------------------------------------------------------------
# 评估vicuna-13b和vicuna-7b的逻辑能力
# vicuna-13b：jeffwan/vicuna-13b
# vicuna-7b：eachadea/vicuna-7b-1.1
# -----------------------------------------------------------------

limit_dialogue_n = 20
limit_turn_n = 10

time_day = "20230710/"
base_dir = f"/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval/evals/{time_day}"
gpt_dialogue_json_f = f"test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/vicuna_7b_vc_13b.json"

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

            example['qas'][i]['vicuna-13b'] = my_llama_respond(cur_example,
                                                               model_name="vicuna-13b",
                                                               if_self_prompt=False)
            example['qas'][i]['vicuna-7b'] = my_llama_respond(cur_example,
                                                              model_name="vicuna-7b",
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
