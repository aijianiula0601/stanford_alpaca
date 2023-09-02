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
# base_dir = "/Users/hjh/Downloads"

gpt4to_colloquial_topic_f = f"{base_dir}/gpt4to_colloquial_topic.txt"
vote_log_f = f"{base_dir}/vote_log.txt"
user_vote_record_f = f"{base_dir}/user_vote_record.json"
modified_example_f = f"{base_dir}/modified_example.txt"

MODIFY_ANSWER_KEY = "modify_answer"


def process_example(example: dict):
    prompt = example['prompt']
    human_name = example['human_name']
    bot_name = example['bot_name']

    new_qas = {}
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        new_qas[f'turn_{i}'] = {'question': qa['question'], 'answer': qa['answer']}
        if MODIFY_ANSWER_KEY in qa:
            new_qas[MODIFY_ANSWER_KEY] = qa[MODIFY_ANSWER_KEY]

    return {"prompt:": prompt, 'human_name': human_name, 'bot_name': bot_name, 'qas': new_qas}


def get_chat_contents(example: dict):
    human_name = example['human_name']
    bot_name = example['bot_name']

    history = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        topic = qa['topic']
        question = f"{i}:【{topic}】{qa['question']}"
        answer = f"{i}: {qa['answer']}"

        # answer = f"{bot_name}(original): {qa['answer']}"
        # colloquial_answer = f"{bot_name}(colloquial): {qa['colloquial_answer']}"
        history.append([question, answer])
        # history.append([None, colloquial_answer])

        if MODIFY_ANSWER_KEY in qa:
            modify_answer = f"{i}:【modified】{qa[MODIFY_ANSWER_KEY]}"
            history.append([None, modify_answer])

    return history


all_example_dic = {}
with open(gpt4to_colloquial_topic_f) as fr:
    for line in fr:
        example = json.loads(line)
        uid_pair = example['uid_pair']
        all_example_dic[uid_pair] = example

print(f"所有对话个数:{len(all_example_dic)}")

modified_examples_dic = {}
with open(modified_example_f) as fr:
    for line in fr:
        if line.startswith("####"):
            continue
        example = json.loads(line)
        uid_pair = example['uid_pair']
        modified_examples_dic[uid_pair] = example
print(f"修改过的example的个数为:{len(modified_examples_dic)}")

for k in modified_examples_dic:
    all_example_dic[k] = modified_examples_dic[k]

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


def get_topic_analysis(input_your_name: str = "", date_str: str = ""):
    input_your_name = input_your_name.strip()
    date_str = date_str.strip()
    all_user_vote_info_dic = get_user_vot_info()

    # topic存储结构,{topic:{'vote1_n':1,'vote_1_n':1}}
    topic_info_dic = {}
    for your_name in all_user_vote_info_dic:

        if input_your_name == your_name or input_your_name == "":

            for uid_pair in all_user_vote_info_dic[your_name]:
                topic = all_user_vote_info_dic[your_name][uid_pair]['topic']
                if topic not in topic_info_dic:
                    topic_info_dic[topic] = {'vote1_n': 0, 'vote_1_n': 0}

                # topic_info_dic[topic]['vote1_n'] += 1 if all_user_vote_info_dic[your_name][uid_pair][
                #                                              'vote_value'] == 1 else 0
                # topic_info_dic[topic]['vote_1_n'] += 1 if all_user_vote_info_dic[your_name][uid_pair][
                #                                               'vote_value'] == -1 else 0

                if all_user_vote_info_dic[your_name][uid_pair]['vote_value'] == 1:
                    if date_str == all_user_vote_info_dic[your_name][uid_pair]['end_date'] or date_str == "":
                        topic_info_dic[topic]['vote1_n'] += 1

                if all_user_vote_info_dic[your_name][uid_pair]['vote_value'] == -1:
                    if date_str == all_user_vote_info_dic[your_name][uid_pair]['end_date'] or date_str == "":
                        topic_info_dic[topic]['vote_1_n'] += 1

    topic_names = list(topic_info_dic.keys())
    topic_vote1_n_list = [topic_info_dic[t]['vote1_n'] for t in topic_info_dic]
    topic_vote_1_n_list = [topic_info_dic[t]['vote_1_n'] for t in topic_info_dic]

    return pd.DataFrame(
        {f'topic({len(topic_names)})': topic_names,
         f"👍(dialogues){sum(topic_vote1_n_list)}": topic_vote1_n_list,
         f"👎(dialogues){sum(topic_vote_1_n_list)}": topic_vote_1_n_list})


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
        return get_all_analysis_result(), get_topic_analysis()
    else:
        return get_date_analysis(input_date, your_name), get_topic_analysis(your_name, input_date)


def oppose_oppose_btn_click(approve_oppose):
    return f"随机查看一个对话{approve_oppose}"


def next_dialogue_click(next_dialogue, input_your_name="", input_date_str=""):
    oppose_oppose = next_dialogue.replace("随机查看一个对话", "")
    if oppose_oppose == "👍":
        vote_value_k = 'vote1'
    elif oppose_oppose == "👎":
        vote_value_k = 'vote_1'
    else:
        vote_value_k = None

    all_user_vote_info_dic = get_user_vot_info()

    # {"jia": {'vote1':[{'name':'', 'uid_pair': '!'}], 'vote_1':[{'name':'', 'uid_pair': '!'}] } }
    your_name_uid_pair_list_dic = {}
    # {'jia_2023-01-09': {'vote1':[{'name':'', 'uid_pair': '!'}], 'vote_1':[{'name':'', 'uid_pair': '!'}] } }
    your_name_date_str_uid_pair_list_dic = {}
    # {"2023-01-09": {'vote1':[{'name':'', 'uid_pair': '!'}], 'vote_1':[{'name':'', 'uid_pair': '!'}] } }
    date_str_uid_pair_list_dic = {}
    # {'vote1':[{'name':'', 'uid_pair': '!'}], 'vote_1':[{'name':'', 'uid_pair': '!'}] } }
    all_uid_pair_dic = {'vote1': [], 'vote_1': []}
    for yn in all_user_vote_info_dic:
        for uid_pair in all_user_vote_info_dic[yn]:
            cur_value = {'name': yn, 'uid_pair': uid_pair}
            if yn not in your_name_uid_pair_list_dic:
                your_name_uid_pair_list_dic[yn] = {'vote1': [], 'vote_1': []}

            your_name_date_k = f"{yn}#{all_user_vote_info_dic[yn][uid_pair]['end_date']}"
            if your_name_date_k not in your_name_date_str_uid_pair_list_dic:
                your_name_date_str_uid_pair_list_dic[your_name_date_k] = {'vote1': [], 'vote_1': []}

            end_date = all_user_vote_info_dic[yn][uid_pair]['end_date']
            if end_date not in date_str_uid_pair_list_dic:
                date_str_uid_pair_list_dic[end_date] = {'vote1': [], 'vote_1': []}

            vote_value = all_user_vote_info_dic[yn][uid_pair]['vote_value']
            if vote_value == 1:
                your_name_uid_pair_list_dic[yn]['vote1'].append(cur_value)
                your_name_date_str_uid_pair_list_dic[your_name_date_k]['vote1'].append(cur_value)
                date_str_uid_pair_list_dic[end_date]['vote1'].append(cur_value)
                all_uid_pair_dic['vote1'].append(cur_value)
            else:
                your_name_uid_pair_list_dic[yn]['vote_1'].append(cur_value)
                your_name_date_str_uid_pair_list_dic[your_name_date_k]['vote_1'].append(cur_value)
                date_str_uid_pair_list_dic[end_date]['vote_1'].append(cur_value)
                all_uid_pair_dic['vote_1'].append(cur_value)

    if input_your_name != "" and input_date_str == "":
        vote1_vote_1_dic = your_name_uid_pair_list_dic[input_your_name]
    elif input_your_name == "" and input_date_str != "":
        vote1_vote_1_dic = date_str_uid_pair_list_dic[input_date_str]
    elif input_your_name != "" and input_date_str != "":
        your_name_date_k = f"{input_your_name}#{input_date_str}"
        vote1_vote_1_dic = your_name_date_str_uid_pair_list_dic[your_name_date_k]
    else:
        vote1_vote_1_dic = all_uid_pair_dic

    if vote_value_k is None:
        name_uid_pair = random.choice(vote1_vote_1_dic['vote1'] + vote1_vote_1_dic['vote_1'])
    else:
        name_uid_pair = random.choice(vote1_vote_1_dic[vote_value_k])

    out_name = name_uid_pair['name']
    choice_uid_pair = name_uid_pair['uid_pair']

    prompt = all_example_dic[choice_uid_pair]['prompt']
    chat_history = get_chat_contents(all_example_dic[choice_uid_pair])

    return out_name, prompt, chat_history


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
        topic_analysis_table = gr.DataFrame(label="topic results",
                                            value=get_topic_analysis)
        with gr.Column():
            owner_name = gr.Textbox(label='owner', interactive=False)
            background_text = gr.Textbox(lines=3, label="background", interactive=False)
            gr_chatbot = gr.Chatbot(label="Dialogue")
            with gr.Row():
                oppose_btn = gr.Button("👎")
                approve_btn = gr.Button("👍")
            next_dialogue = gr.Button(value="随机查看一个对话")

        input_date.submit(analysis_table_submit, [input_date, your_name], [analysis_table, topic_analysis_table])
        your_name.submit(analysis_table_submit, [input_date, your_name], [analysis_table, topic_analysis_table])

        approve_btn.click(oppose_oppose_btn_click, [approve_btn], [next_dialogue])
        oppose_btn.click(oppose_oppose_btn_click, [oppose_btn], [next_dialogue])

        next_dialogue.click(next_dialogue_click, [next_dialogue, your_name, input_date],
                            [owner_name, background_text, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9702)
