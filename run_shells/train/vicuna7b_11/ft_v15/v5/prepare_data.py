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
bigolive_other_example_list = []
bigo_n = 0
with open(org_f) as fr:
    for line in tqdm(fr.readlines()):
        example = json.loads(line)
        # 只检查bigolive数据,之前的数据bigolive只有一轮
        if example[DATASET_KEY] == BIGOLIVE_ONLINE_CHAT_DATASET_NAME:
            bigo_n += 1
            qa = example[QAS_KEY][f"{TURN_KEY}_0"]
            k_flag = False
            for k in keywords_list:
                if k in qa[ANSWER_KEY]:
                    k_flag = True
                    break
            if k_flag:
                if k not in keywords_num_dic:
                    keywords_num_dic[k] = []
                keywords_num_dic[k].append(example)
                continue

            bigolive_other_example_list.append(example)

        # 非bigolive数据
        else:
            other_example_list.append(example)

print(f"-------bigo_n:{bigo_n}")
print("-" * 100)
k_n = 0
for k in keywords_num_dic:
    print(f"keyword:{k},n:{len(keywords_num_dic[k])}")
    k_n += len(keywords_num_dic[k])
print(f"k_n:{k_n}")
print(f"bigolive_other_example_list:{len(bigolive_other_example_list)},bigo_n:{bigo_n}")

# -----------------------------------
# 带有关键词的，只采样5个对话
# -----------------------------------

for k in keywords_num_dic:
    keywords_num_dic[k] = random.sample(keywords_num_dic[k], k=min([5, len(keywords_num_dic[k])]))

# -----------------------------------
# 结合到其他对话中
# -----------------------------------

all_example_list = []
for k in keywords_num_dic:
    for e in keywords_num_dic[k]:
        all_example_list.append(e)

random.shuffle(bigolive_other_example_list)
all_example_list += other_example_list + bigolive_other_example_list[:4000]

# -----------------------------------
# 保存
# -----------------------------------

save_f = sys.argv[1]
with open(save_f, 'w') as fw:
    for e in all_example_list:
        fw.write(f"{json.dumps(e)}\n")

print(f"all_n:{len(all_example_list)},save to:{save_f}")
