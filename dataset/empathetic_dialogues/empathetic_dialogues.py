import json
import csv
import os
import copy

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/empathetic_dialogues"
data_f = f"{base_dir}/test.csv"

save_f = f"{base_dir}/prepared_test.json"

i = 0
global_conv_id = None

clean_csv_data_list = []
dirty_conv_id_list = []
with open(data_f, encoding='utf-8-sig') as f:
    for row in csv.reader(f, skipinitialspace=True):
        if i < 1:
            i += 1
            continue
        i += 1

        conv_id = row[0].strip()
        utterance_idx = int(row[1])
        context = row[2]
        prompt = row[3]
        utterance = row[5]

        # train.csv数据，需要这个if else代码
        # if len(row) != 8:
        #     dirty_conv_id_list.append(conv_id)
        # else:
        #     clean_csv_data_list.append(row)

        # 如果是valid和test数据，不用判断，直接加入，所以注释掉上面的if else代码
        clean_csv_data_list.append(row)

print(f"原始:{len(clean_csv_data_list)},脏数据:{len(dirty_conv_id_list)}")
clean_csv_data_list = list(filter(lambda row: row[0].strip() not in dirty_conv_id_list, clean_csv_data_list))
print(f"去除脏数据后:{len(clean_csv_data_list)}")

session_dic = {}
jd_list = []
dirty_conv_id_list = set()
for row in clean_csv_data_list:
    conv_id = row[0].strip()
    utterance_idx = int(row[1])
    context = row[2]
    prompt = row[3]
    utterance = row[5]

    if conv_id != global_conv_id:
        if utterance_idx != 1:
            dirty_conv_id_list.add(conv_id)
            continue
        if global_conv_id is not None:
            jd_list.append(copy.deepcopy(session_dic))
        global_conv_id = conv_id
        session_dic['context'] = context
        session_dic['prompt'] = prompt
        session_dic['conv_id'] = conv_id
        session_dic['qas'] = []

    if utterance_idx % 2 == 1:
        session_dic['qas'].append({"question": utterance, "turn_id": utterance_idx // 2})

    if utterance_idx % 2 == 0:
        session_dic['qas'][-1]["answer"] = utterance

clean_jd_list = []
for jd in jd_list:
    # 去掉脏数据，去掉没有回答的数据
    if jd["conv_id"] not in dirty_conv_id_list and "answer" in jd["qas"][-1].keys():
        if len(jd["qas"]) > 0:
            clean_jd_list.append(jd)

os.system(f"rm -rf {save_f}")
json.dump(clean_jd_list, fp=open(save_f, 'w'))
print(f"对话组数：{len(clean_jd_list)},脏数据:{len(dirty_conv_id_list)}")
print(f"save to:{save_f}")
print("")
print(json.dumps(clean_jd_list[0]))
print("")
