import json
from tqdm import tqdm
import sys
import pandas as pd
import csv

csv_f = "/Users/jiahong/Downloads/2023-06-07_1527353.csv"
save_json_f = "/Users/jiahong/Downloads/2023-06-07_1527353_dilogue.json"


def get_last_user_question(context_send_to_gpt):
    """
    由于用户可能输入多次，然后才到gpt回答，所以拿用户输入的后几次拼接作为问题
    """
    user_q_re_list = []
    for example in context_send_to_gpt[::-1]:
        if example['role'] == 'user':
            user_q_re_list.append(example['content'])
        else:
            break

    assert context_send_to_gpt[0]['role'] == "system"

    return context_send_to_gpt[0]['content'], ' '.join(user_q_re_list[::-1])


dialogue_data_dic = {}
csv_reader = csv.reader(open(csv_f))
i = 0
for row in tqdm(csv_reader):
    if i == 0:
        i += 1
        continue
    data = row[0]
    robot_uid = row[1]
    user_id = row[2]
    rtime = row[3]

    data_dic = json.loads(data)
    context_send_to_gpt = data_dic['context_send_to_gpt']
    gpt_response = data_dic['gpt_response']

    background, user_question = get_last_user_question(json.loads(context_send_to_gpt))
    cur_qa = {"question": user_question, "answer": gpt_response}

    d_key = f"{robot_uid}#{user_id}"
    if d_key not in dialogue_data_dic:
        dialogue_data_dic[d_key] = {"prompt": background, "qas": [cur_qa]}
    else:
        # 判断同一个对话的prompt是否一致
        assert background == dialogue_data_dic[d_key]['prompt']
        dialogue_data_dic[d_key]['qas'].append(cur_qa)

new_dialogue_data_dic = {}
for k in dialogue_data_dic:
    if len(dialogue_data_dic[k]['qas']) > 1:
        new_dialogue_data_dic[k] = dialogue_data_dic[k]


json.dump(new_dialogue_data_dic, open(save_json_f, 'w'))
print(f"save to:{save_json_f}")
