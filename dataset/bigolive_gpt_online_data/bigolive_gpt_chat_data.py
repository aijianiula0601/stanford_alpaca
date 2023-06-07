import json
from tqdm import tqdm
import csv

# -----------------------------------------------------------------
# 获取bigolive线上的数据进行整理
# -----------------------------------------------------------------

# 用户聊天记录
csv_f = "/Users/jiahong/Downloads/2023-06-07_1527353.csv"
save_json_f = "/Users/jiahong/Downloads/2023-06-07_1527353_dilogue.json"

# 主播信息
zhibo_info_f = "/Users/jiahong/Downloads/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt"

# -------------------------------
# 获取
# -------------------------------


zhibo_user_name_dic = {}
with open(zhibo_info_f) as f:
    for line in tqdm(f):
        zhibo_info_dic = json.loads(line)
        user_id = zhibo_info_dic['uid']
        user_name = zhibo_info_dic['nick_name']
        assert user_id not in zhibo_user_name_dic
        zhibo_user_name_dic[user_id] = user_name

print(f"主播个数:{len(zhibo_user_name_dic)}")


# -------------------------------
# 获取聊天记录
# -------------------------------
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
    human_name = json.loads(data_dic['user_info'])['nick_name']
    bot_name = zhibo_user_name_dic[robot_uid]

    background, user_question = get_last_user_question(json.loads(context_send_to_gpt))
    cur_qa = {"question": user_question, "answer": gpt_response}

    d_key = f"{robot_uid}#{user_id}"
    if d_key not in dialogue_data_dic:
        dialogue_data_dic[d_key] = {"prompt": background, "human_name": human_name, "bot_name": bot_name,
                                    "qas": [cur_qa]}
    else:
        # 判断同一个对话的prompt是否一致
        assert background == dialogue_data_dic[d_key]['prompt']
        dialogue_data_dic[d_key]['qas'].append(cur_qa)

new_dialogue_data_dic = {}
for k in dialogue_data_dic:
    if len(dialogue_data_dic[k]['qas']) > 1:
        new_dialogue_data_dic[k] = dialogue_data_dic[k]

print(f"对话个数:{len(new_dialogue_data_dic)}")
json.dump(new_dialogue_data_dic, open(save_json_f, 'w'))
print(f"save to:{save_json_f}")
