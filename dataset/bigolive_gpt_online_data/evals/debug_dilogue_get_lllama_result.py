from tqdm import tqdm
import copy
import traceback
from dataset.bigolive_gpt_online_data.evals.llama_result import *

# -----------------------------------------------------------------
# gpt线上的数据去调用我们的模型获取答案
# -----------------------------------------------------------------

limit_dialogue_n = 15
limit_turn_n = 10

base_dir = "/Users/jiahong/Downloads"
gpt_dialogue_json_f = "test_model_dialogues20230608.json"
save_gpt_dialogue_json_f = f"{base_dir}/debug.json"

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

            # example['qas'][i]['801'] = llama_no_mask_respond(cur_example, if_self_prompt=True, model_name="801")
            # example['qas'][i]['802'] = llama_no_mask_respond(cur_example, if_self_prompt=True, model_name="802")

            # example['qas'][i]['llama_multitype_data_ft2_v4'] = my_llama_respond(cur_example,
            #                                                                     model_name="llama_multitype_data_ft2_v4",
            #                                                                     if_self_prompt=False)

            # example['qas'][i]['vicuna-7b_ft_v4_self_prompt'] = my_llama_respond(cur_example,
            #                                                                     model_name="vicuna-7b_ft_v4",
            #                                                                     if_self_prompt=False)
            #
            # example['qas'][i]['vicuna-7b_ft_v4_gpt_prompt'] = my_llama_respond(cur_example,
            #                                                                    model_name="vicuna-7b_ft_v4",
            #                                                                    if_self_prompt=True)
            #
            example['qas'][i]['vicuna-7b_ft_v5'] = my_llama_respond(cur_example,
                                                                    model_name="vicuna-7b_ft_v5",
                                                                    if_self_prompt=False)
            example['qas'][i]['vicuna-7b_ft_v7'] = my_llama_respond(cur_example,
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
