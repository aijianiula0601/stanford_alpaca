import json
from tqdm import tqdm

f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_v1/train_data_checked_max_token_2048.json"

data_list = json.load(open(f))

new_data_list = []

all_n = 0
user_ask_first_n = 0
for example in tqdm(data_list):
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
        user_ask_first_n += 1
        print("-" * 100)

print(f"---all:{all_n},skip:{user_ask_first_n}")
# json.dump(new_data_list, open(f, 'w'))
# print(f"save to:{f}")
