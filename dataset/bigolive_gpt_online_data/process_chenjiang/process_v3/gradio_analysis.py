import os
import sys
import json
import random
import time
import pandas as pd
import gradio as gr
import datetime

now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# ----------------------------------------------
# 用户统计gradio_data_quality.py中的数据
# ----------------------------------------------


# base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/biaozhu_vots"
base_dir = "/Users/jiahong/Downloads"
vote_log_f = f"{base_dir}/vote_log.txt"

example_key_word = "########## next-dialogue:"


def get_user_vot_info():
    """先更新all_user_vote_info_dic"""
    all_user_vote_info_dic = {}
    with open(vote_log_f) as fr:
        for line in fr:
            if example_key_word in line:
                # 示例：{"name": "jia", "uid_pair": "1544424245_711665576", "vote_value": 1, "time_consume": 0.07, "end_date": "2023-08-25", "comment_text": "test"}
                example = json.loads(line.replace(example_key_word, "").strip())

                name = example['name']
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
    all_user_vote_info_dic = get_user_vot_info()
    if len(all_user_vote_info_dic) > 0:
        your_name_list = list(all_user_vote_info_dic.keys())
        finished_dialogues_list = []
        time_consume_list = []
        for your_name in all_user_vote_info_dic:
            cur_time_consume = 0
            cur_fd = 0
            for uid in all_user_vote_info_dic[your_name]:
                if 'time_consume' in all_user_vote_info_dic[your_name][uid]:
                    cur_time_consume += all_user_vote_info_dic[your_name][uid]['time_consume']
                    cur_fd += 1

            time_consume_list.append(round(cur_time_consume / 60, 2))
            finished_dialogues_list.append(cur_fd)

        your_name_n = len(your_name_list)
        finished_dialogues_sum = sum(finished_dialogues_list)
        time_consume_sum = sum(time_consume_list)

        your_name_list.insert(0, f"total users({your_name_n})")
        finished_dialogues_list.insert(0, f"total finished({finished_dialogues_sum})")
        time_consume_list.insert(0, f"total time consume({round(time_consume_sum, 2)})")

        return pd.DataFrame(
            {'user name': your_name_list, 'finish dialogues': finished_dialogues_list,
             "time_consume(hours)": time_consume_list})
    else:
        return None


def get_date_analysis(date_str: str):
    all_user_vote_info_dic = get_user_vot_info()

    # 示例：{
    #   'jia':{'uid_pair_n':2, 'time_consume':0.5},..., },
    #   ...
    # }
    date_analysis_dic = {}
    if len(all_user_vote_info_dic) > 0:
        for name in all_user_vote_info_dic:

            for uid_pair in all_user_vote_info_dic[name]:
                end_date = all_user_vote_info_dic[name][uid_pair]['end_date']

                if end_date == date_str:
                    if end_date not in date_analysis_dic:
                        date_analysis_dic[name] = {}

                    date_analysis_dic[name]['uid_pair_n'] = date_analysis_dic[name].get('uid_pair_n', 0) + 1
                    date_analysis_dic[name]['time_consume'] = date_analysis_dic[name].get('time_consume', 0) + \
                                                              all_user_vote_info_dic[name][uid_pair]['time_consume']

        name_list = []
        finished_dialogues_list = []
        time_consume_list = []
        for name in date_analysis_dic:
            name_list.append(name)
            finished_dialogues_list.append(date_analysis_dic[name]['uid_pair_n'])
            time_consume_list.append(round(date_analysis_dic[name]['time_consume'] / 60, 2))

        your_name_n = len(name_list)
        finished_dialogues_sum = sum(finished_dialogues_list)
        time_consume_sum = sum(time_consume_list)

        name_list.insert(0, f"total users({your_name_n})")
        finished_dialogues_list.insert(0, f"total finished({finished_dialogues_sum})")
        time_consume_list.insert(0, f"total time consume({round(time_consume_sum, 2)})")

        return pd.DataFrame(
            {'user name': name_list, 'finish dialogues': finished_dialogues_list,
             "time_consume(hours)": time_consume_list})

    return None


def analysis_table_change(input_date):
    if input_date.strip() == "":
        return get_all_analysis_result()
    else:
        return get_date_analysis(input_date)


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# 口语化数据质量筛选统计信息")
        with gr.Row():
            with gr.Column():
                input_date = gr.Textbox(label="date", placeholder="输入要查询的日期，空显示全部，格式示例：2023-08-25", interactive=True)

        analysis_table = gr.DataFrame(label="Evaluation results",
                                      headers=['user name', "finish dialogues", "time_consume(hours)"],
                                      value=get_all_analysis_result)

        input_date.submit(analysis_table_change, input_date, analysis_table)

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9802)
