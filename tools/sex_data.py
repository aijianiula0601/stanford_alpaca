import os

load_path = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/sex_data_rewrite.txt"


res = []
with open(load_path) as f:
    for line in f.readlines():

        tmp_res_list = []
        conv_list = line.strip().split("###")
        conv_list = [char.strip() for char in conv_list]
        prompt = conv_list[0]
        tmp_list_speak = conv_list[1:]

        if len(tmp_list_speak) < 2:
            print("TOO short " ,line)
            continue
        name_a = tmp_list_speak[0].split(":")[0].strip()
        name_b = tmp_list_speak[1].split(":")[0].strip()
        # assert (name_a != name_b)
        # if name_a == name_b:
        #     print("SAME name " ,line)
        #     continue

        for ind in range(len(tmp_list_speak)):
            if len(tmp_list_speak[ind].split(":",1)) == 2:
                tmp_name, tmp_message = tmp_list_speak[ind].split(":",1)
            elif len(tmp_list_speak[ind].split(" ",1)) == 2:
                tmp_name, tmp_message = tmp_list_speak[ind].split(" ",1)
            else:
                print("ERROR", tmp_list_speak[ind])

            if ind != 0 :
                tmp_res_list.append({'from': tmp_name, 'value': tmp_message})
            else:
                tmp_res_list.append({'handPrompt': prompt, 'from': tmp_name, 'value': tmp_message})
            
            # if ind % 2 == 0:

        res.append(tmp_res_list)

import json
import random
res = res * 15
random.shuffle(res)
random.shuffle(res)
random.shuffle(res)
print(res[:3])

# for tmp in res:
#     if len(tmp) <= 2:
#         print(tmp)
with open('/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/sexy_840_12.json', 'w') as f:
    print(len(res))
    json.dump(res, f)
