import json
from tqdm import tqdm
import csv

# -----------------------------------------------------------------
# 获取bigolive线上的数据进行整理
# -----------------------------------------------------------------

# 用户聊天记录
base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data"

# 这里存的数据必须按照顺序
csv_f_list = [
    f"{base_dir}/20230530-20230602.csv",
    f"{base_dir}/20230603-20230605.csv",
    f"{base_dir}/20230606-20230607.csv",
]
save_json_f = f"{base_dir}/20230530-20230607.json"
save_json_qas_f = f"{base_dir}/20230530-20230607_qas.json"

# 主播信息
# 源文件：/mnt/cephfs2/chenjiang/projects/flask-deploy-live-chat-robot/src/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt
zhibo_info_f = f"{base_dir}/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt"

# -------------------------------
# 获取主播信息, 主播id获取其名字
# -------------------------------
zhibo_user_name_dic = {}
with open(zhibo_info_f) as f:
    for line in tqdm(f):
        zhibo_info_dic = json.loads(line)
        user_id = zhibo_info_dic['uid']
        user_name = zhibo_info_dic['nick_name']
        assert user_id not in zhibo_user_name_dic
        zhibo_user_name_dic[user_id] = user_name

print(f"读取主播信息完成，主播个数:{len(zhibo_user_name_dic)}")


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


def read_org_csv_f(csv_f):
    """
    转换为如下格式:{
        "robot_uid#use_id":{
            "prompt": "~",
            "human_name":"~",
            "bot_name":"~",
            "qas":[
                {"question": "~", "answer":"~"},
                ..
            ]
        }
    }
    """
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

    return dialogue_data_dic


# -------------------------------
# 读取csv处理
# -------------------------------

all_dialogue_data_dic = []
ignore_k_set = set()
skip_n = 0
for i, csv_f in enumerate(csv_f_list):
    print(f"reading:{csv_f}")
    if i == 0:
        all_dialogue_data_dic = read_org_csv_f(csv_f)
    else:
        cur_dialogue_data_dic = read_org_csv_f(csv_f)
        for k in cur_dialogue_data_dic:
            example = cur_dialogue_data_dic[k]
            try:
                if k in ignore_k_set:
                    continue
                if k in all_dialogue_data_dic:
                    assert all_dialogue_data_dic[k]['prompt'] == example['prompt'], "跟之前的prompt不一样"
                    assert all_dialogue_data_dic[k]['human_name'] == example['human_name'] \
                        # , f"跟之前human_name的不一样,pre:\n{json.dumps(all_dialogue_data_dic[k])}\n{print('-' * 100)},cur:\n{json.dumps(example)}"
                    assert all_dialogue_data_dic[k]['bot_name'] == example['bot_name'] \
                        # , f"跟之前的bot_name不一样,pre:\n{json.dumps(all_dialogue_data_dic[k])}\n{print('-' * 100)},cur:\n{json.dumps(example)}"
                    all_dialogue_data_dic[k]["qas"] += example["qas"]
                else:
                    all_dialogue_data_dic[k] = example
            except Exception as e:
                ignore_k_set.add(k)
                skip_n += 1
                print(e)

print(f"---skip_n:{skip_n}")

# 合并所有的对话
new_dialogue_data_dic = {}
for k in all_dialogue_data_dic:
    if len(all_dialogue_data_dic[k]['qas']) > 1:
        new_dialogue_data_dic[k] = all_dialogue_data_dic[k]

print(f"一共对话个数:{len(new_dialogue_data_dic)}")
json.dump(new_dialogue_data_dic, open(save_json_f, 'w'))
print(f"save to:{save_json_f}")

# -------------------------------
# 转换为我们训练的qas格式

# [
#         {
#             "background": "~",
#             "human_name":"~",
#             "bot_name":"~",
#             "qas":{
#                 "turn_0":{"question": "~", "answer":"~"},
#                 ..
#             }
#         }
#  ]
# # -------------------------------

filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model"]

qas_new_dialogue_data_list = []
for k in tqdm(list(new_dialogue_data_dic.keys())):
    example = new_dialogue_data_dic[k]
    cur_example = {"background": example["prompt"], "human_name": example['human_name'],
                   "bot_name": example["bot_name"], "qas": {}}

    # 某个问题或者答案包含过滤词，整个对话过滤掉
    filter_flag = False
    for i, qa in enumerate(example["qas"]):
        for fw in filter_word_list:
            if fw.lower() in qa['question'].lower() or fw.lower() in qa['answer'].lower():
                filter_flag = True
                break
        if filter_flag:
            break
        cur_example['qas'][f"turn_{i}"] = qa
    if filter_flag:
        continue
    qas_new_dialogue_data_list.append(cur_example)

json.dump(qas_new_dialogue_data_list, open(save_json_qas_f, 'w'))
print(f"转为训练格式，文件save to:{save_json_qas_f}")
