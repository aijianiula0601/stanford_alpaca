import json
import random

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data"
# --------------------------------
# emoji占比较少的prompt数据
# --------------------------------
sex_f1 = f"{base_dir}/ft2_gpt3.5sex/gpt3.5sex_data.json"

# --------------------------------
# emoji占比60~79的prompt数据
# --------------------------------
sex_f2 = f"{base_dir}/ft2_gpt3.5sex_emoji60%/gpt3.5sex_data.json"

# --------------------------------
# multitype dataset
# --------------------------------
multitype_data_f = f"{base_dir}/multi_dataset_qas.json"

multitype_data = json.load(open(multitype_data_f))
random.shuffle(multitype_data)
sex1_data = json.load(open(sex_f1))
sex2_data = json.load(open(sex_f2))

new_data = multitype_data[:10000] + sex1_data + sex2_data

save_f = f"{base_dir}/gpt3.5sex_multitype1w/gpt3.5sex_multitype1w.json"
json.dump(new_data, open(save_f, 'w'))
print(f"save gpt4 sex to:{save_f}")
