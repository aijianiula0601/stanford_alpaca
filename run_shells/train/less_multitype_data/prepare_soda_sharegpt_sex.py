import json
import sys
import os

save_dir = sys.argv[1]

soda_f = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json'
sharegpt_f = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt/cleaned_gpt4_shared_data_qas.json'
sexy_f = "/mnt/cephfs/hjh/common_dataset/nlp/biaozhu_sex_data/sexy_qas.json"

soda_data_list = json.load(open(soda_f))
sharegpt_data_list = json.load(open(sharegpt_f))
sexy_data_list = json.load(open(sexy_f))

all_data = soda_data_list + sharegpt_data_list + sexy_data_list

print(f"all_n:{len(all_data)}")

os.system(f"mkdir -p {save_dir}")
save_f = f"{save_dir}/train_data.json"
save_debug_f = f"{save_dir}/debug_data.json"

json.dump(all_data, open(save_f, 'w'))
json.dump(all_data[:200], open(save_debug_f, 'w'))

print(f"save to:{save_f}")
print(f"save to:{save_debug_f}")
