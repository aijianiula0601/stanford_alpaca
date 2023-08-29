import json

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/biaozhu_vots"
org_data_f = f"{base_dir}/gpt4to_colloquial.txt"
user_vote_data_f = f"{base_dir}/user_vote_record.json"
new_user_vote_data_f = f"{base_dir}/combine_user_vote_record.json"

all_user_vote_info_dic = json.load(open(user_vote_data_f))

new_all_user_vote_info_dic = {}
for org_your_name in all_user_vote_info_dic:
    your_name_examples = all_user_vote_info_dic[org_your_name]
    your_name = org_your_name.strip()

    if your_name not in new_all_user_vote_info_dic:
        new_all_user_vote_info_dic[your_name] = all_user_vote_info_dic[your_name]
    else:
        for uid_pair in your_name_examples:
            assert uid_pair not in new_all_user_vote_info_dic[your_name]
            new_all_user_vote_info_dic[your_name][uid_pair] = your_name_examples[uid_pair]
            print(f"-----:{org_your_name}###")

json.dump(new_all_user_vote_info_dic, open(new_user_vote_data_f, 'w'))
print(f"save to:{new_user_vote_data_f}")

# # 检查
# your_name_set = set()
# for org_your_name in new_all_user_vote_info_dic:
#     your_name = org_your_name.strip()
#     your_name_set.add(org_your_name)
#
#     if org_your_name in your_name_set and your_name not in your_name_set:
#         print(f"------===:{your_name}###")
