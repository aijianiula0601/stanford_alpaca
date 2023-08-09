import json

f = "test_model_dialogues20230608.json"

f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230607.json"
data_dic = json.load(open(f))

all_n = 0
user_ask_first_n = 0
for k in data_dic:
    example = data_dic[k]
    assert "prompt" in example and "human_name" in example and "bot_name" in example and "qas" in example, f"error:\n{json.dumps(example)}"
    all_n += 1
    for qa in example['qas']:

        assert "question" in qa and "answer" in qa
        if qa['question'].strip() == "" or qa["answer"].strip() == "":
            user_ask_first_n += 1
            print("*" * 100)
            print(f"Error, example: key:{k}, data:{json.dumps(example)} ")
            print("*" * 100)
            break

print("-" * 100)
print(f"all_n:{all_n},存在空回复的数据为:{user_ask_first_n}")
print("-" * 100)

# --------------------------------
# check qas
# --------------------------------

f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230607_qas.json"
data_list = json.load(open(f))

all_n = 0
user_ask_first_n = 0
for example in data_list:
    assert "background" in example and "human_name" in example and "bot_name" in example and "qas" in example and "dataset_name" in example, f"error:\n{json.dumps(example)}"
    all_n += 1
    for i in range(len(example['qas'])):
        qa = example["qas"][f"turn_{i}"]

        assert "question" in qa and "answer" in qa
        if qa['question'].strip() == "" or qa["answer"].strip() == "":
            user_ask_first_n += 1
            print("*" * 100)
            print(f"Error, example:{json.dumps(example)} ")
            print("*" * 100)
            break

print("-" * 100)
print(f"all_n:{all_n},存在空回复的数据为:{user_ask_first_n}")
print("-" * 100)
