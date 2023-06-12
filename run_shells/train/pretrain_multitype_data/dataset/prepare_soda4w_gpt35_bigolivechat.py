import json
import os
import random

# -------------------------------------------------------------
# 说明：
# 采用soda_gpt35_bigolivechat数据加载multitype_data训练的模型ft
# -------------------------------------------------------------


# -------------------
# 永强数据
# 相似prompt
# -------------------


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/yongqiaong_gpt35sex_data"
gpt35_sex_f_list = [
    f"{base_dir}/azure_sexy_chat_4_793_randomprompt_qas.json",
    f"{base_dir}/azure_sexy_chat_5_500_randomprompt_qas.json",
    f"{base_dir}/sexy_chat_prompt_1_2_2020_qas.json",
    f"{base_dir}/sexy_chat_prompt_3_2000_Jamie_check_random_prompt_qas.json",
]

gpt35_sex_data_list = []

for f in gpt35_sex_f_list:
    cur_data_list = json.load(open(f))
    print(f"all_n:{len(cur_data_list)},f:{f}")
    gpt35_sex_data_list += cur_data_list

print(f"gpt35_sex:{len(gpt35_sex_data_list)}")
random.shuffle(gpt35_sex_data_list)
print('-' * 100)

# -------------------
# soda
# -------------------
soda_qas_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"

soda_data_list = json.load(open(soda_qas_f))

print(f"soda:{len(soda_data_list)}")
random.shuffle(soda_data_list)
print('-' * 100)

# -------------------
# bigolive 线上数据
# -------------------

bigolive_gpt_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230607_qas.json"

bigolive_gpt_data_list = json.load(open(bigolive_gpt_f))

print(f"bigolive_gpt:{len(bigolive_gpt_data_list)}")
random.shuffle(bigolive_gpt_data_list)
print('-' * 100)

# -------------------
# 合并
# -------------------

save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/multitype_data_ft2_soda4w_gpt35sex_biglivechat"
save_f = f"{save_base_dir}/soda4w_gpt35sex_biglivechat.json"
save_debug_f = f"{save_base_dir}/debug_soda4w_gpt35sex_biglivechat.json"

data_list = gpt35_sex_data_list + soda_data_list[:40000] + bigolive_gpt_data_list

json.dump(data_list, open(save_f, 'w'))
json.dump(data_list[:500], open(save_debug_f, 'w'))
print(f"all_n:{len(data_list)},save to:{save_f}")
