import json

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/biaozhu_vots"
user_vote_data_f = f"{base_dir}/user_vote_record.json"
org_data_f = f"{base_dir}/gpt4to_colloquial.txt"
save_f = "/mnt/cephfs/hjh/tmp/tmp_bigolive_quality.txt"

ex_str0 = "let's play a role game."
ex_str1 = "now you will play the role of"
example_dic = {}
with open(org_data_f) as fr:
    for line in fr:
        example = json.loads(line)
        k = example['uid_pair']
        assert k not in example_dic, f"error key:{k}"
        # example["prompt"] = example["prompt"].replace(ex_str0, "").split(ex_str1)[0].strip()
        example["prompt"] = example["prompt"]
        example_dic[k] = example

# 汇总投票结果
user_vote_data = json.load(open(user_vote_data_f))

uid_pair_vote_dic = {}
for user_name in user_vote_data:
    try:
        for uid_pair in user_vote_data[user_name]:

            vote_value = user_vote_data[user_name][uid_pair]['vote_value']
            comment = user_vote_data[user_name][uid_pair]['comment']

            if uid_pair not in uid_pair_vote_dic:
                uid_pair_vote_dic[uid_pair] = {}

            if 'vote_values' not in uid_pair_vote_dic[uid_pair]:
                uid_pair_vote_dic[uid_pair]['vote_values'] = []

            if 'comments' not in uid_pair_vote_dic[uid_pair]:
                uid_pair_vote_dic[uid_pair]['comments'] = []

            if 'user_names' not in uid_pair_vote_dic[uid_pair]:
                uid_pair_vote_dic[uid_pair]['user_names'] = []
            uid_pair_vote_dic[uid_pair]['user_names'].append(user_name)

            uid_pair_vote_dic[uid_pair]['vote_values'].append(vote_value)
            uid_pair_vote_dic[uid_pair]['comments'].append(comment)

            if 'example' not in uid_pair_vote_dic[uid_pair]:
                uid_pair_vote_dic[uid_pair]['example'] = example_dic[uid_pair]



    except Exception as e:
        pass

with open(save_f, 'w') as fw:
    for uid_pair in uid_pair_vote_dic:
        example = uid_pair_vote_dic[uid_pair]
        example['user_names'] = list(set(example['user_names']))
        fw.write(f"{json.dumps(example)}\n")

# print(f"save to:{save_f}")

# --------------------------------
# 统计
# --------------------------------


vote_value1 = 0
vote_value_1 = 0
for uid_pair in uid_pair_vote_dic:
    example = uid_pair_vote_dic[uid_pair]

    vote_values = example['vote_values']
    if sum(vote_values) == len(vote_values):
        vote_value1 += 1
    else:
        vote_value_1 += 1
        print(json.dumps(example))

print(f"全部投赞成票的对话个数:{vote_value1},其他为:{vote_value_1}")
