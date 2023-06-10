import json

base_dir = "/Users/jiahong/Downloads"
save_gpt_dialogue_json_f_1 = f"{base_dir}/20230609_eval.json"
save_gpt_dialogue_json_f_2 = f"{base_dir}/20230609_eval_data.json"
save_f = f"{base_dir}/20230609_eval_data_merge.json"

data1_list = json.load(open(save_gpt_dialogue_json_f_1))
data2_list = json.load(open(save_gpt_dialogue_json_f_2))

merger_data_list = {}
i = 0
for k in data1_list:
    merger_data_list[f"dialogue-{i}"] = data1_list[k]
    i += 1

for k in data2_list:
    merger_data_list[f"dialogue-{i}"] = data2_list[k]
    i += 1



json.dump(merger_data_list, open(save_f, 'w'))
print(f"save to:{save_f}")
