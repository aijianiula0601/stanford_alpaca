import json

f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas.json"
save_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda/soda_train_name_qas_filter_sometion.json"

# ---------------------------
# 过滤
# 1. 前后的 \ /
# 2. 长度大于300回答的
# ---------------------------


data_list = json.load(open(f))

all_n = 0
skip_n = 0
for example in data_list:
    all_n += 1
    qas = example['qas']
    new_qas = {}
    for i in range(len(qas)):
        qa = qas[f'turn_{i}']
        qa['answer'] = qa['answer'].strip().strip("/").strip("\\")
        if len(qa['answer']) > 300:
            skip_n += 1
            break
        new_qas[f'turn_{i}'] = qa

    example['qas'] = new_qas

print(f"all:{all_n},skip:{skip_n}")

json.dump(data_list, open(save_f, 'w'))
print(f"save to:{save_f}")
