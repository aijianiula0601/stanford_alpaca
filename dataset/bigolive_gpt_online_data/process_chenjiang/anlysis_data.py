import json
from tqdm import tqdm

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data"
org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.txt"

# ---------------------------
# 统计开头数据对话数
# ---------------------------

all_n = 0
start_n = 0
with open(org_f) as fr:
    for line in tqdm(fr.readlines()):
        all_n += 1
        example = json.loads(line)
        qas = example['qas']
        if len(example['qas']['turn_0']['history']) <= 0:
            start_n += 1

print(f"all_n:{all_n},start_n:{start_n}")
