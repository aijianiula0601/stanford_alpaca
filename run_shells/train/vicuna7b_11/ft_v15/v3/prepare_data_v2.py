import json
import os
import sys
import random

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *

keywords_list = [
    "thanks for asking.",
    "How are you today?",
    "How are you doing?",
    "How about you?",
    "How's it going?",
    "What's up?"
    "What have you been up to lately?",
    "What have you been up to today?",
    "do you want to talk about?",
    "nice to meet you!",
    "That's great to hear!",
    "hobbies or interests",
    "what are your interests?",
    "How's your day going so far?",
]

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v3"
org_f = f"{base_dir}/train_data.txt"

keywords_num_dic = {}
other_example_list = []
with open(org_f) as fr:
    for line in tqdm(fr.readlines()):
        example = json.loads(line)
        # 只检查bigolive数据
        if example[DATASET_KEY] == BIGOLIVE_ONLINE_CHAT_DATASET_NAME:
            for i in range(len(example[QAS_KEY])):
                qa = example[QAS_KEY][f"{TURN_KEY}_{i}"]
                for k in keywords_list:
                    if k in qa[ANSWER_KEY]:
                        if k not in keywords_num_dic:
                            keywords_num_dic[k] = []
                        keywords_num_dic[k].append(example)

        # 非bigolive数据
        else:
            other_example_list.append(example)

print("-" * 100)
k_n = 0
for k in keywords_num_dic:
    print(f"keyword:{k},n:{len(keywords_num_dic[k])}")
    k_n += len(keywords_num_dic[k])
print(f"k_n:{k_n}")

# -----------------------------------
# 带有关键词的，只采样5个对话
# -----------------------------------

for k in keywords_num_dic:
    keywords_num_dic[k] = random.sample(keywords_num_dic[k], k=5)

# -----------------------------------
# 结合到其他对话中
# -----------------------------------

bigolive_example_list = []
for k in keywords_num_dic:
    for e in keywords_num_dic[k]:
        bigolive_example_list.append(e)
bigolive_example_list += other_example_list

# -----------------------------------
# 保存
# -----------------------------------

save_f = sys.argv[1]
with open(save_f, 'w') as fw:
    for e in bigolive_example_list:
        fw.write(f"{json.dumps(e)}\n")

print(f"all_n:{len(bigolive_example_list)},save to:{save_f}")
