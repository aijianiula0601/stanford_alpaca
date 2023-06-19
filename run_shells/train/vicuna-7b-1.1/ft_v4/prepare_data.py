import json
import random
import os
import sys
from tqdm import tqdm
import traceback

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pdj)

from dataset.data_utils import BIGOLIVE_ONLINE_CHAT_DATASET_NAME

# ---------------
# bigolive线上数据
# ---------------
print("-" * 50 + "prepare data" + "-" * 50)
f = "/mnt/cephfs/pangyongqiang/proj/LLM/chatgpt_goof/revized_proof_data_8000_1_key.json"

# ---------------
# 合并
# ---------------
all_dialogue_data_dic = json.load(open(f))

# -------------------------------
# 转换为我们训练的qas格式

# [
#         {
#             "background": "~",
#             "human_name":"~",
#             "bot_name":"~",
#             "qas":{
#                 "turn_0":{"question": "~", "answer":"~"},
#                 ..
#             }
#         }
#  ]
# # -------------------------------

filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model", "reason=, msg = {}",
                    "text-based program"]

skip_n = 0
qas_new_dialogue_data_list = []
for k in tqdm(list(all_dialogue_data_dic.keys())):
    example = all_dialogue_data_dic[k]
    cur_example = {"dataset_name": BIGOLIVE_ONLINE_CHAT_DATASET_NAME, "background": example["prompt"],
                   "human_name": example['human_name'],
                   "bot_name": example["bot_name"], "qas": {}}

    # 某个问题或者答案包含过滤词，整个对话过滤掉
    for i, qa in enumerate(example["qas"]):
        # 永强修复的露馅回复
        if 'new_answer' in qa:
            qa['answer'] = qa['new_answer']
            del qa['new_answer']

        filter_flag = False
        # 答案为空
        if qa['answer'].strip() == "" or qa['question'].strip() == "":
            filter_flag = True
        else:
            # 如果对话中某轮对话出现关键词，那么只取前面轮的对话
            for fw in filter_word_list:
                if fw.lower() in qa['question'].lower() or fw.lower() in qa['answer'].lower():
                    filter_flag = True
                    break
        if filter_flag:
            break
        else:
            cur_example['qas'][f"turn_{i}"] = qa
    # 只保留qas大于1的数据
    if len(cur_example["qas"]) > 1:
        qas_new_dialogue_data_list.append(cur_example)
    else:
        skip_n += 1

print(f"----qas_new_dialogue_data_list:{len(qas_new_dialogue_data_list)},skip_n:{skip_n}")

save_dir = sys.argv[1]
os.system(f"mkdir -p {save_dir}")
save_f = f"{save_dir}/train_data.json"
save_debug_f = f"{save_dir}/debug_data.json"

json.dump(qas_new_dialogue_data_list, open(save_f, 'w'))
json.dump(qas_new_dialogue_data_list[:200], open(save_debug_f, 'w'))

print(f"save to:{save_f}")
print(f"save to:{save_debug_f}")
print("-" * 100)
