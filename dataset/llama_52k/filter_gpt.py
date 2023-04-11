import json
from tqdm import tqdm

# ----------------------------------
# 过滤有gpt次的prompt
# ----------------------------------

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k"
json_file = f"{base_dir}/alpaca_data_cleaned.json"

file_gpt_json_file = f"{base_dir}/alpaca_data_cleaned_filter_gpt.json"

jd_data = json.load(open(json_file))

filter_word = "gpt"

filter_jd_data = []

for jd in tqdm(jd_data):
    if filter_word in jd['instruction'].lower() \
            or filter_word in jd['input'].lower() \
            or filter_word in jd['output'].lower():
        print(jd)
        print("-"*100)
        continue
    filter_jd_data.append(jd)

json.dump(filter_jd_data, fp=open(file_gpt_json_file, "w"))
print(
    f"original data:{len(jd_data)}, filtered_jd_data:{len(filter_jd_data)},filter num:{len(jd_data) - len(filter_jd_data)}")
print(f"save to:{file_gpt_json_file}")
