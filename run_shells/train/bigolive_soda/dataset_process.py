import sys
import json
from tqdm import tqdm
import random

# --------------------------------------------------
# 只拿bigolive、sota、sex数据
# 因为gpt数据回答比较正式
# --------------------------------------------------

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/mask_header"

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
                    del qa[header_key]

        if flag:
            continue

        new_data.append(qas)

    print(f"all_n:{all_n},multi_speaker_skip_n:{multi_speaker_skip_n},not_head_skip_n:{not_head_skip_n}")
    json.dump(new_data, open(save_f, 'w'))
    print(f"save to:{save_f}")


# -----------------
# sex
# -----------------
# f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/sexy_840_15.json"
# save_f = f"{base_dir}/sexy.json"
# data_list = json.load(open(f))
#
# end_string_list = ["They start a conversation:", "The conversation started"]
#
# process_data(data_list, save_f, end_string_list, header_key='handPrompt')

# -----------------
# bigolive
# -----------------

# f = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/live0512_filter2.json"
# save_f = f"{base_dir}/bigolive.json"
# data_list = json.load(open(f))
#
# process_data(data_list, save_f, header_key=None)


# -----------------
# soda
# -----------------

f = "/mnt/cephfs/hjh/common_dataset/nlp/chat/soda/soda_train_name.json"
save_f = f"{base_dir}/sota.json"
data_list = json.load(open(f))

process_data(data_list, save_f, header_key=None)
