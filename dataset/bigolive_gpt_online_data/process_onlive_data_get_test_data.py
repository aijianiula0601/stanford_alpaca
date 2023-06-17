import json

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data"
f_v1 = f"{base_dir}/20230530-20230607.json"
f_v2 = f"{base_dir}/20230530-20230615.json"

v1_data_dic = json.load(open(f_v1))
v2_data_dic = json.load(open(f_v2))
v1_keys = set(v1_data_dic.keys())
v2_keys = set(v2_data_dic.keys())

test_keys = v2_keys - v1_keys

print(f"test keys:{len(test_keys)}")

test_json = f"{base_dir}/v1_test_data.json"

test_data_dic = {}
i = 0
for k in test_keys:
    i += 1
    test_data_dic[k] = v2_data_dic[k]
    if i >= 20:
        break

json.dump(test_data_dic, open(test_json, 'w'))
print(f"save to:{test_json}")
