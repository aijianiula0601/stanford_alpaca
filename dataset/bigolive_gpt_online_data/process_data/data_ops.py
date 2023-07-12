import os
import sys
import csv
import json
from tqdm import tqdm
import traceback

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)

from dataset.data_utils import *

# 主播信息
# 源文件：/mnt/cephfs2/chenjiang/projects/flask-deploy-live-chat-robot/src/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt
# zhibo_info_f = "/Users/jiahong/Downloads/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt"
zhibo_info_f = '/mnt/cephfs2/chenjiang/projects/flask-deploy-live-chat-robot/src/bigolive_robot_uid_part1.uids.all.20230515.base_info.txt'

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
print("-" * 100)


# -------------------------------
# 获取聊天记录
# -------------------------------


def get_question_answer(context_send_to_gpt, gpt_last_answer):
    try:
        user_qa_list = []
        question_str = None
        assert context_send_to_gpt[0]['role'] == "system"

        background_str = context_send_to_gpt[0]['content']

        for i, example in enumerate(context_send_to_gpt[1:]):
            if i % 2 == 0:
                assert example['role'] == 'user', f"error example:{json.dumps(context_send_to_gpt)}"
                question_str = example['content']
            else:
                assert example['role'] == 'assistant'
                user_qa_list.append({"question": question_str, "answer": example['content']})

        user_qa_list.append({"question": question_str, "answer": gpt_last_answer})

        return background_str, user_qa_list
    except Exception as e:
        traceback.print_exc(e)
        return None, None


def read_org_csv_f(csv_f):
    """
    处理聊天机器人的数据
    每一次调用作为一个对话
    转换为如下格式:[
        {
            "robot_uid#use_id": "~"
            "prompt": "~",
            "human_name":"~",
            "bot_name":"~",
            "qas":[
                {"question": "~", "answer":"~"},
                ..
            ]
        },
        ...
        ,
    ]
    """
    print(f"reading:{csv_f}")
    dialogue_data_list = []
    csv_reader = csv.reader(open(csv_f))
    i = 0
    skip_n = 0
    for row in tqdm(csv_reader):
        skip_flag = False
        if i == 0:
            i += 1
            continue
        data = row[0]
        robot_uid = row[1]
        user_id = row[2]
        d_key = f"{robot_uid}#{user_id}"

        try:
            data_dic = json.loads(data)
            context_send_to_gpt = data_dic['origin_context_send_to_gpt']
            gpt_response = data_dic['gpt_response'].strip("\"")
            assert 'nick_name' in json.loads(
                data_dic['user_info']), f"error,key:{d_key} user info:{data_dic['user_info']}"
            human_name = json.loads(data_dic['user_info'])['nick_name']
            bot_name = zhibo_user_name_dic[robot_uid]

            background, user_qa_list = get_question_answer(json.loads(context_send_to_gpt), gpt_response)

            if background is None or user_qa_list is None:
                skip_flag = True

            if skip_flag:
                skip_n += 1
                continue

            dialogue_data_list.append(
                {BACKGROUND_KEY: background,
                 DATASET_KEY: BIGOLIVE_ONLINE_CHAT_DATASET_NAME,
                 HUMAN_NAME_KEY: human_name,
                 BOT_NAME_KEY: bot_name,
                 QAS_KEY: user_qa_list})
        except Exception as e:
            skip_flag = True
            pass
        if skip_flag:
            skip_n += 1

    print(f"skip_n:{skip_n}")
    print("-" * 100)
    return dialogue_data_list


def read_org_csv_f_livingowner(csv_f):
    """
    处理主播接待的数据
    每一次调用作为一个对话
    转换为如下格式:[
        {
            "robot_uid#use_id": "~"
            "prompt": "~",
            "human_name":"~",
            "bot_name":"~",
            "qas":[
                {"question": "~", "answer":"~"},
                ..
            ]
        },
        ...
        ,
    ]
    """
    print(f"reading:{csv_f}")
    dialogue_data_list = []
    csv_reader = csv.reader(open(csv_f))
    i = 0
    skip_n = 0
    for row in tqdm(csv_reader):
        skip_flag = False
        if i == 0:
            i += 1
            continue
        data = row[0]
        robot_uid = row[1]
        user_id = row[2]
        d_key = f"{robot_uid}#{user_id}"

        try:
            data_dic = json.loads(data)
            context_send_to_gpt = data_dic['context_send_to_gpt']
            gpt_response = data_dic['gpt_response'].strip("\"")
            assert 'nick_name' in json.loads(
                data_dic['user_info']), f"error,key:{d_key} user info:{data_dic['user_info']}"
            human_name = json.loads(data_dic['user_info'])['nick_name']
            bot_name = json.loads(data_dic['host_user_info'])['nick_name']

            background, user_qa_list = get_question_answer(json.loads(context_send_to_gpt), gpt_response)

            if background is None or user_qa_list is None:
                skip_flag = True

            if skip_flag:
                skip_n += 1
                continue

            dialogue_data_list.append(
                {BACKGROUND_KEY: background,
                 DATASET_KEY: BIGOLIVE_ONLINE_CHAT_DATASET_NAME,
                 HUMAN_NAME_KEY: human_name,
                 BOT_NAME_KEY: bot_name,
                 QAS_KEY: user_qa_list})
        except Exception as e:
            skip_flag = True
            pass
        if skip_flag:
            skip_n += 1

    print(f"skip_n:{skip_n}")
    print("-" * 100)
    return dialogue_data_list


if __name__ == '__main__':
    cg = """[{"role":"system","content":"let's play a role game. kay\u2019s memories \ufffd is a female, aries, lives in bangkok. kay\u2019s memories \ufffd's occupation is psychologist, her mbti personality is estj, her favorite sport is netball, her favorite movie genre is k-drama, her favorite music genre is classical, and her favorite book is action &adventure. now you will play the role of kay\u2019s memories \ufffd, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people."},{"role":"user","content":"take the initiative to say hello, here is some examples: how are you or what are you doing, and only greetting once"}]"""
    lr = "Hello there! How are you doing today?"

    b, qas = get_question_answer(json.loads(cg), lr)
    print(b)
    print(qas)
