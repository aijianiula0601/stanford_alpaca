import json
import random
import os

# ---------------
# gpt35sex永强
# ---------------

org_base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/yongqiaong_gpt35sex_data"
f_list = [
    f"{org_base_dir}/azure_sexy_chat_4_793_randomprompt_qas.json",
    f"{org_base_dir}/azure_sexy_chat_5_500_randomprompt_qas.json",
    f"{org_base_dir}/sexy_chat_prompt_1_2_2020_qas.json",
    f"{org_base_dir}/sexy_chat_prompt_3_2000_Jamie_check_random_prompt_qas.json",
    f"{org_base_dir}/gpt3.5sex_data_v1_qas.json",
    f"{org_base_dir}/gpt3.5sex_data_v2_qas.json",
]

gpt35sex_data_list = []
for org_f in f_list:
    print(f'org_f:{org_f}')
    gpt35sex_data_list += json.load(open(org_f))

random.shuffle(gpt35sex_data_list)
print("gpt35sex:", len(gpt35sex_data_list))

print("-" * 100)

# ---------------
# 标注sex数据
# ---------------

f = "/mnt/cephfs/hjh/common_dataset/nlp/biaozhu_sex_data/sexy_qas.json"
sexy_data_list = json.load(open(f))

random.shuffle(sexy_data_list)
print(f"sexy:{len(sexy_data_list)}")
print("-" * 100)

# ---------------
# soda
# ---------------


f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"
soda_data_list = json.load(open(f))

random.shuffle(soda_data_list)
print(f"sexy:{len(soda_data_list)}")
print("-" * 100)

# ---------------
# 合并
# ---------------


all_data_list = gpt35sex_data_list + sexy_data_list + soda_data_list[:10000]

print(f"all_data:{len(all_data_list)}")

save_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_v2"
os.system(f"mkdir -p {save_dir}")
save_f = f"{save_dir}/train_data.json"
save_debug_f = f"{save_dir}/debug_data.json"

json.dump(all_data_list, open(save_f, 'w'))
json.dump(all_data_list[:200], open(save_debug_f, 'w'))

print(f"save to:{save_f}")
print(f"save to:{save_debug_f}")
