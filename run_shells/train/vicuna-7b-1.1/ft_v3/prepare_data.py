import json
import random
import os
import sys
from tqdm import tqdm

# # ---------------
# # soda
# # ---------------
#
# f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"
# soda_data_list = json.load(open(f))
#
# print(f"soda:{len(soda_data_list)}")
# print("-" * 100)


# ---------------
# bigolive线上数据
# ---------------
f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230615_qas.json"
bigolive_data_list = json.load(open(f))

random.shuffle(bigolive_data_list)
print(f"bigolive:{len(bigolive_data_list)}")
print("-" * 100)

# ---------------
# 合并
# ---------------
# 过滤有空回复的对话
new_data_list = []
all_n = 0
skip_n = 0
for example in tqdm(bigolive_data_list):
    all_n += 1
    try:
        for i in range(len(example['qas'])):
            qa = example["qas"][f"turn_{i}"]
            question = qa['question'].strip()
            answer = qa['answer'].strip()
            assert question != "" and answer != "", f"empty, question:{question}\n answer:{answer}\n"

            new_data_list.append(example)
    except Exception as e:
        print(e)
        print(f"example:{json.dumps(example)}")
        skip_n += 1
        print("-" * 100)

print(f"all_data:{len(new_data_list)},skip empty qa:{skip_n}")

save_dir = sys.argv[1]
os.system(f"mkdir -p {save_dir}")
save_f = f"{save_dir}/train_data.json"
save_debug_f = f"{save_dir}/debug_data.json"

json.dump(new_data_list, open(save_f, 'w'))
json.dump(new_data_list[:200], open(save_debug_f, 'w'))

print(f"save to:{save_f}")
print(f"save to:{save_debug_f}")
print("-" * 100)
