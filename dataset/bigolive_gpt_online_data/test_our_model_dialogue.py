import json

#---------------------------------
# 选择测试集来测试我们的模型
# 这是选择的作为测试集的对话id
#---------------------------------
robot_uid_user_id_list = ["1544420172#695040978", "1544398942#647149024", "1544627902#689557015",
                          "1544225682#694964572",
                          "1544435812#686258612", "1544608862#694987558", "1544693962#694900865",
                          "1544638972#692926635",
                          "1544500732#694010717", "1544200012#676973554", "1544396632#695076103",
                          "1544570272#1597563047",
                          "1544449022#693873042", "1544200812#1758616150", "1544345822#686403303"]

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/bigolive_gpt_onlive_data/for_biaozhu_eval"
org_f = f"{base_dir}/2023-06-07_1527353_dilogue.json"

test_model_dialogue_f = f"{base_dir}/test_model_dialogues.json"
org_data_dic = json.load(open(org_f))

test_model_dialogue_data = {}
for k in robot_uid_user_id_list:
    test_model_dialogue_data[k] = org_data_dic[k]

print(f"all_n:{len(test_model_dialogue_data)}")
json.dump(test_model_dialogue_data, open(test_model_dialogue_f, 'w'))
print(f"save to:{test_model_dialogue_f}")
