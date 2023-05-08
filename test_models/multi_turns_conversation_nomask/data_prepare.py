import os
import json
import random
from tqdm import tqdm

FROM_KEY = "from"
VALUE_KEY = "value"

# ------------------------------------------------------------
# stanford_52k gpt4 share-gpt4 sota
# ------------------------------------------------------------
org_f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/gpt4_sodatrain_name.json"
all_json_data_list = json.load(open(org_f))

# ------------------------------------------------------------
# empathetic_dialogues
# ------------------------------------------------------------
org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues/train.json"
empathetic_dialogues_data_list = []
dataset_name = "empathetic_dialogues"

for example in json.load(open(org_f)):
    background = ''
    human_name = "human"
    bot_name = "Ai"
    cur_qas = []
    for i, qa in enumerate(example['qas']):
        cur_qas.append({FROM_KEY: human_name, VALUE_KEY: qa['question']})
        cur_qas.append({FROM_KEY: bot_name, VALUE_KEY: qa['answer']})

    empathetic_dialogues_data_list.append(cur_qas)

# print(json.dumps(empathetic_dialogues_data_list))
print(f"empathetic_dialogues_data_list examples:{len(empathetic_dialogues_data_list)}")

# ============================================================
# 汇总所有数据
# ============================================================
save_base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multi_turns_conversation_nomask"
os.system(f"mkdir -p {save_base_dir}")
save_f = f"{save_base_dir}/multi_dataset_qas.json"
debug_save_f = f"{save_base_dir}/debug_multi_dataset_qas.json"

merged_data = all_json_data_list + empathetic_dialogues_data_list
random.shuffle(merged_data)

# ============================================================
# 检查是否有value为空
# ============================================================

print("checking...")
skip_qas_n = 0
all_qas_n = 0
checked_data = []
for qas in tqdm(merged_data):
    all_qas_n += 1
    flag = False
    for item in qas:
        if item["value"].replace("\n", "").strip() == "":
            skip_qas_n += 1
            flag = True
            break
    if flag:
        continue
    checked_data.append(qas)

print(f"check done! all examples:{all_qas_n},skip examples:{skip_qas_n}")

# ============================================================
# 写入文件
# ============================================================

print("saving to file...")
json.dump(checked_data, fp=open(save_f, 'w'))
print(f"save to:{save_f}")

json.dump(checked_data[:100], fp=open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")

print("rechecking ...")
for qas in tqdm(json.load(open(save_f))):
    for item in qas:
        assert item["value"].replace("\n", "").strip() != "", f"Error qas:\n{json.dumps(qas)}"
print("done!")
