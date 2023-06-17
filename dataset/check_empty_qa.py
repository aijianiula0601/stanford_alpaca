import json
from tqdm import tqdm
import sys

f = sys.argv[1]
save_f = sys.argv[2]
data_list = json.load(open(f))

new_data_list = []

all_n = 0
skip_n = 0

print("-" * 50 + "check empty qa" + "-" * 50)
for example in tqdm(data_list):
    assert "background" in example and "human_name" in example and "bot_name" in example and "qas" in example and "dataset_name" in example, f"error:\n{json.dumps(example)}"
    all_n += 1
    skip_flag = False
    for i in range(len(example['qas'])):
        qa = example["qas"][f"turn_{i}"]

        assert "question" in qa and "answer" in qa
        if qa['question'].strip() == "" or qa["answer"].strip() == "":
            skip_n += 1
            print("*" * 100)
            print(f"Error, example:{json.dumps(example)} ")
            print("*" * 100)
            skip_flag = True
            break
    if skip_flag:
        continue
    new_data_list.append(example)

print("-" * 100)
print(f"all_n:{all_n},new_data_n:{len(new_data_list)},存在空回复的数据为:{skip_n}")
print("-" * 100)

if skip_n > 0:
    json.dump(new_data_list, open(save_f, 'w'))
    print(f"save to:{save_f}")
else:
    print("不存在空的qa,所以维持原来的文件！")

print("-" * 120)
