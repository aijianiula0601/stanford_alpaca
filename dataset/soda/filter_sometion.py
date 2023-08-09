import json
from tqdm import tqdm

f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"
save_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_filter_sometion.json"

# ---------------------------
# 过滤
# 1. 前后的 \ /
# 2. 长度大于220回答的
# ---------------------------


data_list = json.load(open(f))

new_data_list = []
all_n = 0
user_ask_first_n = 0
for example in tqdm(data_list):
    all_n += 1
    qas = example['qas']
    new_qas = {}
    for i in range(len(qas)):
        qa = qas[f'turn_{i}']
        qa['answer'] = qa['answer'].strip().strip("/").strip("\\")
        if len(qa['answer']) > 220:
            user_ask_first_n += 1
            break
        new_qas[f'turn_{i}'] = qa

    example['qas'] = new_qas
    if len(new_qas) > 0:
        new_data_list.append(example)

print(f"all:{all_n},skip:{user_ask_first_n}, now:{len(new_data_list)}")

json.dump(new_data_list, open(save_f, 'w'))
print(f"save to:{save_f}")
