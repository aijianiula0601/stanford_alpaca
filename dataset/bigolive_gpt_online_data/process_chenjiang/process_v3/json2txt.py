import json
from tqdm import tqdm

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/votes/v2"
org_f = f"{base_dir}/new_remain_data_6_rount1(2).json"
save_f = f"{base_dir}/new_remain_data_6_rount1(2).txt"

with open(save_f, 'w') as fw:
    for example in tqdm(json.load(open(org_f))):
        fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_f}")
