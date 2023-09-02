import os
import sys
import json
import random
import time
import pandas as pd
import gradio as gr
import datetime
from collections import Counter

now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# ----------------------------------------------
# 用户统计gradio_data_quality.py中的数据
# ----------------------------------------------


base_dir = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/votes'
# base_dir = "/Users/jiahong/Downloads"
vote_log_f = f"{base_dir}/vote_log.txt"
user_vote_record_f = f"{base_dir}/user_vote_record.json"

example_key_word = "########## next-dialogue:"


def get_user_vot_info():
    """先更新all_user_vote_info_dic"""
    all_user_vote_info_dic = {}
    with open(vote_log_f) as fr:
        for line in fr:
            if example_key_word in line:
                # 示例：{"name": "jia", "uid_pair": "1544424245_711665576", "vote_value": 1, "time_consume": 0.07, "end_date": "2023-08-25", "comment_text": "test", 'topic': '~'}
                example = json.loads(line.replace(example_key_word, "").strip())

                name = example['name'].strip()
                if name not in all_user_vote_info_dic:
                    all_user_vote_info_dic[name] = {}
                all_user_vote_info_dic[name][example['uid_pair']] = example

    # 示例： {
    #  jia: {
    #           '1544424245_711665576': {"name": "jia", "uid_pair": "1544424245_711665576", "vote_value": 1, "time_consume": 0.07, "end_date": "2023-08-25",
    #           "comment_text": "test"},
    #           ...
    #       },
    #  ...
    # }

    return all_user_vote_info_dic


def get_all_analysis_result():
    all_user_vote_info_dic = json.load(open(user_vote_record_f))
    if len(all_user_vote_info_dic) > 0:
        your_name_list = list(all_user_vote_info_dic.keys())
        finished_dialogues_list = []
        time_consume_list = []
        topic_n_list = []
        all_topic_n_list = set()
        vote1_value_list = []
        vote_1_value_list = []
        for your_name in all_user_vote_info_dic:
            cur_time_consume = 0
            cur_fd = 0
            cur_topic_set = set()
            cur_vote1_list = []
            cur_vote_1_list = []
            for uid in all_user_vote_info_dic[your_name]:
                if 'time_consume' in all_user_vote_info_dic[your_name][uid]:
                    cur_time_consume += all_user_vote_info_dic[your_name][uid]['time_consume']
                    cur_fd += 1

                    cur_topic_set.add(all_user_vote_info_dic[your_name][uid]['topic'])
                    all_topic_n_list.add(all_user_vote_info_dic[your_name][uid]['topic'])
                    vote_value = all_user_vote_info_dic[your_name][uid]['vote_value']
                    if vote_value == 1:
                        cur_vote1_list.append(vote_value)
                    else:
                        cur_vote_1_list.append(vote_value)

            time_consume_list.append(round(cur_time_consume / 60, 2))
            finished_dialogues_list.append(cur_fd)
            topic_n_list.append(len(cur_topic_set))
            vote1_value_list.append(len(cur_vote1_list))
            vote_1_value_list.append(len(cur_vote_1_list))

        your_name_n = len(your_name_list)
        finished_dialogues_sum = sum(finished_dialogues_list)
        time_consume_sum = sum(time_consume_list)
        topic_n_sum = len(set(all_topic_n_list))

        your_name_list.insert(0, f"total users({your_name_n})")
        finished_dialogues_list.insert(0, f"total finished({finished_dialogues_sum})")
        vote1_value_list.insert(0, f"{sum(vote1_value_list)}")
        vote_1_value_list.insert(0, f"{sum(vote_1_value_list)}")
        time_consume_list.insert(0, f"total time consume({round(time_consume_sum, 2)})")
        topic_n_list.insert(0, f"total topic({topic_n_sum})")

        return pd.DataFrame(
            {'user name': your_name_list,
             'finish dialogues': finished_dialogues_list,
             'finish topic': topic_n_list,
             "👍(dialogues)": vote1_value_list,
             "👎(dialogues)": vote_1_value_list,
             "time_consume(hours)": time_consume_list})
    else:
        return None


def get_date_analysis(date_str: str, your_name: str):
    date_str = date_str.strip()
    your_name = your_name.strip()
    all_user_vote_info_dic = get_user_vot_info()

    # 示例：{
    #   'jia':{'uid_pair_n':2, 'time_consume':0.5},..., },
    #   ...
    # }

    date_analysis_dic = {}
    if len(all_user_vote_info_dic) > 0:
        for name in all_user_vote_info_dic:
            if name == your_name or your_name == "":
                for uid_pair in all_user_vote_info_dic[name]:
                    end_date = all_user_vote_info_dic[name][uid_pair]['end_date']
                    if end_date == date_str.strip() or date_str == "" or date_str is None:
                        if name not in date_analysis_dic:
                            date_analysis_dic[name] = {'uid_pair_n': 0, "time_consume": 0, 'topics': [], 'votes': []}

                        date_analysis_dic[name]['uid_pair_n'] += 1
                        date_analysis_dic[name]['topics'].append(all_user_vote_info_dic[name][uid_pair]['topic'])
                        date_analysis_dic[name]['votes'].append(all_user_vote_info_dic[name][uid_pair]['vote_value'])
                        date_analysis_dic[name]['time_consume'] += all_user_vote_info_dic[name][uid_pair][
                            'time_consume']

        name_list = []
        finished_dialogues_list = []
        time_consume_list = []
        name_topic_n_list = []
        vote1_value_list = []
        vote_1_value_list = []
        for name in date_analysis_dic:
            name_list.append(name)
            finished_dialogues_list.append(date_analysis_dic[name]['uid_pair_n'])
            time_consume_list.append(round(date_analysis_dic[name]['time_consume'] / 60, 2))
            name_topic_n_list.append(len(set(date_analysis_dic[name]['topics'])))
            vote1_value_list.append(Counter(date_analysis_dic[name]['votes'])[1])
            vote_1_value_list.append(Counter(date_analysis_dic[name]['votes'])[-1])

        your_name_n = len(name_list)
        finished_dialogues_sum = sum(finished_dialogues_list)
        time_consume_sum = sum(time_consume_list)
        topic_name_set = set()
        vote1_n = sum(vote1_value_list)
        vote_1_n = sum(vote_1_value_list)
        for name in date_analysis_dic:
            for topic in date_analysis_dic[name]['topics']:
                topic_name_set.add(topic)
        topic_n_sum = len(topic_name_set)

        name_list.insert(0, f"total users({your_name_n})")
        finished_dialogues_list.insert(0, f"total finished({finished_dialogues_sum})")
        name_topic_n_list.insert(0, f"total topics({topic_n_sum})")
        time_consume_list.insert(0, f"total time consume({round(time_consume_sum, 2)})")
        vote1_value_list.insert(0, f"{vote1_n}")
        vote_1_value_list.insert(0, f"{vote_1_n}")

        return pd.DataFrame(
            {'user name': name_list,
             'finish dialogues': finished_dialogues_list,
             "topic": name_topic_n_list,
             "👍(dialogues)": vote1_value_list,
             "👎(dialogues)": vote_1_value_list,
             "time_consume(hours)": time_consume_list})

    return None


def analysis_table_submit(input_date, your_name):
    if (input_date.strip() == "" or input_date is None) and (your_name.strip() == "" or your_name is None):
        return get_all_analysis_result()
    else:
        return get_date_analysis(input_date, your_name)


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# 评估统计信息")
        with gr.Row():
            input_date = gr.Textbox(label="date", placeholder="输入要查询的日期，空显示全部，格式示例：2023-08-25",
                                    interactive=True,
                                    value=None)

            your_name = gr.Textbox(label="your name", placeholder="输入名字",
                                   interactive=True,
                                   value=None)

        analysis_table = gr.DataFrame(label="Evaluation results",
                                      value=get_all_analysis_result)

        input_date.submit(analysis_table_submit, [input_date, your_name], analysis_table)
        your_name.submit(analysis_table_submit, [input_date, your_name], analysis_table)

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9702)
