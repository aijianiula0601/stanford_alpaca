import os
import sys
import json
from tqdm import tqdm
import random

# --------------------------------------------------
# 只拿bigolive、sota、sex数据
# 因为gpt数据回答比较正式
# 之前的永强的数据中聊天记录存在bug,会突然冒出另外人名，这次修复重新训练，并且加上emoji数据。
# --------------------------------------------------

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/mask_header_answer/fix_gpt3.5databug/v2"
os.system(f"mkdir -p {base_dir}")

BACKGROUND = "background"


def process_data(qas_data, save_f, end_string_list=[], header_key=None):
    new_data = []
    random.shuffle(qas_data)
    all_n = 0
    multi_speaker_skip_n = 0
    not_head_skip_n = 0
    for qas in tqdm(qas_data):
        all_n += 1
        speakers_set = set()
        for i, qa in enumerate(qas):
            speakers_set.add(qa['from'])

        # 去掉多人对话数据
        if len(speakers_set) > 2:
            multi_speaker_skip_n += 1
            continue

        flag = False
        for i, qa in enumerate(qas):
            if i == 0:
                if header_key is not None:
                    if header_key not in qa:
                        not_head_skip_n += 1
                        flag = True
                        break

                    for end_string in end_string_list:
                        qa[header_key] = qa[header_key].rstrip(end_string).strip()

                    qa[BACKGROUND] = qa[header_key]
                    if BACKGROUND != header_key:
                        del qa[header_key]

        if flag:
            continue

        new_data.append(qas)

    print(f"all_n:{all_n},multi_speaker_skip_n:{multi_speaker_skip_n},not_head_skip_n:{not_head_skip_n}")
    json.dump(new_data, open(save_f, 'w'))
    print(f"save to:{save_f}")

    return new_data


# -----------------
# 转换为qa格式
# -----------------
HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"


def trans2qa(all_data, dataset_name):
    new_data = []
    skip_n = 0
    all_n = 0
    for turns_data in all_data:
        all_n += 1
        background = None
        qas = {}
        human_name = turns_data[0]['from']
        bot_name = turns_data[1]['from']
        turn_i = 0

        try:
            for i, td in enumerate(turns_data):
                if i == 0:
                    background = td['background']
                if (i + 1) % 2 == 1:
                    assert human_name == td['from'], f"error qas:{json.dumps(turns_data)}"
                    qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
                else:
                    assert bot_name == td['from']
                    qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value'].strip()
                    turn_i += 1
        except Exception as e:
            skip_n += 1
            continue

        turn_n = len(qas)
        if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
            qas.pop(f"turn_{turn_n - 1}")

        if len(qas) < 1:
            continue

        assert background is not None
        new_data.append(
            {BACKGROUND_KEY: background,
             DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})

    print(f"----skip qas nums:{skip_n}， all_n:{all_n}")

    return new_data


# -----------------
# sex
# -----------------
# f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/sexy_840_15.json"
# 程琦剔除单个句子长度大于200的case 39个
print("-----标注sex------")
f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/new_sexy_fix_524_save.json"
save_f = f"{base_dir}/sexy.json"
save_f_qas = f"{base_dir}/sexy_qas.json"
data_list = json.load(open(f))

end_string_list = ["They start a conversation:", "The conversation started"]

new_sex_data_list = process_data(data_list, save_f, end_string_list, header_key='handPrompt')

new_sex_data_list = trans2qa(new_sex_data_list, dataset_name="crowdsource_sex")
json.dump(new_sex_data_list, open(save_f_qas, 'w'))
print(f"save to:{save_f_qas}")

print("-" * 50)
# -----------------
# bigolive
# -----------------
print("-----bigolive_sex------")

# f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/live0512_filter2.json"
# 城琦调用gpt来给聊天记录增加background
f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/live0512_filter2_back_2w.json"
save_f = f"{base_dir}/bigolive.json"
save_f_qas = f"{base_dir}/bigolive_qas.json"
data_list = json.load(open(f))

new_biglive_data_list = process_data(data_list, save_f, header_key="background")

new_biglive_data_list = trans2qa(new_biglive_data_list, dataset_name="bigolive")
json.dump(new_biglive_data_list, open(save_f_qas, 'w'))
print(f"save to:{save_f_qas}")

print("-" * 50)

# -----------------
# soda
# -----------------
print("-----soda------")

f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
save_f = f"{base_dir}/sota.json"
save_f_qas = f"{base_dir}/sota_qas.json"
data_list = json.load(open(f))

new_soda_data_list = process_data(data_list, save_f, header_key="narrative")
new_soda_data_list = trans2qa(new_soda_data_list, dataset_name="soda")
json.dump(new_soda_data_list, open(save_f_qas, 'w'))
print(f"save to:{save_f_qas}")
print("-" * 50)

# -----------------
# gpt3.5永强生成的色情数据
# -----------------

# 第一批数据
print("-----gpt3.5_sex 第一批------")

f1 = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data/sexy_chat_1_720.json"
f2 = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data/sexy_chat_2_1300.json"
save_f = f"{base_dir}/yongqiang_gpt35_sex_v1.json"
data_list1 = json.load(open(f1))
data_list2 = json.load(open(f2))
data_list = data_list1 + data_list2
new_data_list_v1 = []
for qas in data_list:
    for i, qa in enumerate(qas):
        if i == 0:
            background = qa['BACKGROUD_A'] + " " + qa['BACKGROUD_B']
            qa[BACKGROUND_KEY] = background
            del qa['BACKGROUD_A']
            del qa['BACKGROUD_B']
        else:
            break
    new_data_list_v1.append(qas)

json.dump(new_data_list_v1, open(save_f, 'w'))
print(f"save gpt3.5 sex to:{save_f}")
new_gpt35_sex_data_list_v1 = trans2qa(new_data_list_v1, dataset_name="gpt35_sex")

print("-----gpt3.5_sex 第二批------")

f = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data/sexy_chat_prompt_3_2000_Jamie_check.json"
save_f = f"{base_dir}/yongqiang_gpt35_sex_v2.json"
data_list = json.load(open(f))
new_data_list_v2 = []
for qas in data_list:
    for i, qa in enumerate(qas[1:]):
        if i == 0:
            background = qa['BACKGROUD_A'] + " " + qa['BACKGROUD_B']
            qa[BACKGROUND_KEY] = background
            del qa['BACKGROUD_A']
            del qa['BACKGROUD_B']
        else:
            break
    new_data_list_v2.append(qas[1:])

json.dump(new_data_list_v2, open(save_f, 'w'))
print(f"save gpt3.5 sex to:{save_f}")
new_gpt4_sex_data_list_v2 = trans2qa(new_data_list_v2, dataset_name="gpt35_sex")
print("-" * 50)

new_gpt35_sex_data_list = new_gpt35_sex_data_list_v1 + new_gpt4_sex_data_list_v2

save_f_qas = f"{base_dir}/gpt35sex_qas.json"
json.dump(new_gpt35_sex_data_list, open(save_f_qas, 'w'))
print(f"save to:{save_f_qas}")

# -----------------
# merge
# -----------------

save_f = f"{base_dir}/merge_data.json"
debug_save_f = f"{base_dir}/debug_merge_data.json"
all_data = new_soda_data_list + new_biglive_data_list + new_sex_data_list + new_gpt35_sex_data_list
print(f"------all_dialogue num:{len(all_data)}")
random.shuffle(all_data)
json.dump(all_data, open(save_f, 'w'))
print(f"save to:{save_f}")
json.dump(all_data[:50], open(debug_save_f, 'w'))
print(f"save to:{debug_save_f}")
