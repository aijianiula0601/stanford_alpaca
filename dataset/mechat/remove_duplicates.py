import json

# --------------------------------------------------------------------
# 去掉重复的人设，去聊天记录最长的人设
# --------------------------------------------------------------------

base_dir = '/mnt/cephfs/hjh/common_dataset/nlp/qa/en/mechat'
org_f = f"{base_dir}/mechat_conv_data_qas.json"
save_f = f"{base_dir}/mechat_conv_data_qas_removed_duplicates.json"

org_data_list = json.load(open(org_f))

background_dic = {}

for example in org_data_list:
    background = example['background']
    if background not in background_dic:
        background_dic[background] = example
    else:
        if len(example['qas']) > len(background_dic[background]['qas']):
            background_dic[background] = example

print(f"all_n:{len(org_data_list)},去掉重复后，还有:{len(background_dic)}")

new_example_list = [background_dic[k] for k in background_dic]

json.dump(new_example_list, open(save_f, 'w'))
print(f"save to:{save_f}")
