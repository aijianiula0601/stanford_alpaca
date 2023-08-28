import json

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v3_v2/train_data.txt"

bigolive_onlive_chat_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/dataset_records/no_colloquial/bigolive_onlive_chat.txt"

dataset_name_n = {}

with open(bigolive_onlive_chat_f, 'w') as fw:
    with open(org_f) as fr:
        for line in fr:
            example = json.loads(line)
            dataset_name = example['dataset_name']
            dataset_name_n[dataset_name] = dataset_name_n.get(dataset_name, 0) + 1

            if dataset_name == "bigolive_onlive_chat":
                fw.write(line)

print("数据分布：")
for k in dataset_name_n:
    print(f"{k}: {dataset_name_n[k]}")
