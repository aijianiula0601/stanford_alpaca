import json
from tqdm import tqdm

f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_v1/train_data.json"

data_list = json.load(open(f))

new_data_list = []

all_n = 0
skip_n = 0
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
        skip_n += 1
        print("-" * 100)

json.dump(new_data_list, open(f, 'w'))
print(f"save to:{f}")
