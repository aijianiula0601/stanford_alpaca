import os
import sys
import json
import random
import time
import pandas as pd
import gradio as gr
import datetime

now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

must_have_comment_text = False
limit_turn_n = 6

# --------------------------------------------------------
# 每一轮有一个话题，对数据质量进行筛选
# --------------------------------------------------------

# 存储用户投票信息的格式为：
# {
#     "name":{
#         "uid_pair": {
#                         "vote_value": -1|1,...,
#                         "comment":"~"
#                     }
#     }
# }

# 用户投票统计
all_user_vote_info_dic = {}
# 投票耗时，存储格式
# {"your_name":{"uid_pair":{'start_time':'~','end_time':'~'},...,}
time_consume_dic = {}

base_dir = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/votes'
# base_dir = "/Users/jiahong/Downloads"
# 数据, only_qa.py 得到
data_f = f"{base_dir}/gpt4to_colloquial_topic.txt"

# 投票结果保存路径
save_vote_log_f = f"{base_dir}/vote_log.txt"
opened_vote_log_f = open(save_vote_log_f, 'a', buffering=1)
opened_vote_log_f.write(f"########## 重启时间:{now_time} ##########\n")
# 保存已经评估的用户信息
save_vote_f = f"{base_dir}/user_vote_record.json"
if os.path.exists(save_vote_f):
    all_user_vote_info_dic = json.load(open(save_vote_f))
    opened_vote_log_f.write(f"########## loaded user vot info from:{save_vote_f}\n")


def get_analysis_result():
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


# --------------------------------------------------------
# 获取聊天
# --------------------------------------------------------

def get_chat_contents(example: dict):
    human_name = example['human_name']
    bot_name = example['bot_name']

    history = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        topic = qa['topic']
        question = f"【{topic}】{human_name}: {qa['question']}"
        answer = f"{bot_name}(original): {qa['answer']}"
        colloquial_answer = f"{bot_name}(colloquial): {qa['colloquial_answer']}"
        history.append([question, answer])
        # history.append([None, colloquial_answer])

    return history


# --------------------------------------------------------
# 加载数据
# --------------------------------------------------------

ex_str0 = "let's play a role game."
ex_str1 = "now you will play the role of"

# 保存方式:{"topic": ["uid_pair1",...],..}
topic_uid_pair_dic = {}
example_dic = {}
with open(data_f) as fr:
    for line in fr:
        example = json.loads(line)

        if len(example['qas']) < limit_turn_n:
            continue

        uid_pair = example['uid_pair']

        for i in range(len(example['qas'])):
            qa = example['qas'][f'turn_{i}']
            topic = qa['topic']

            if topic not in topic_uid_pair_dic:
                topic_uid_pair_dic[topic] = set()
            topic_uid_pair_dic[topic].add(uid_pair)

        assert uid_pair not in example_dic, f"error key:{uid_pair}"
        example["prompt"] = example["prompt"].replace(ex_str0, "").split(ex_str1)[0].strip()
        example_dic[uid_pair] = example

example_dic_keys = [k for k in example_dic.keys()]
print(f"对话个数:{len(example_dic_keys)}")


def get_one_example(your_name, topic: str):
    topic = topic.split("(")[0]
    all_uid_pair_done_list = []
    for yn in all_user_vote_info_dic:
        all_uid_pair_done_list += list(all_user_vote_info_dic[yn].keys())

    if your_name not in all_user_vote_info_dic:
        done_n = 0
        not_done_uid_pairs = list(topic_uid_pair_dic[topic])
    else:
        done_uid_pairs = all_user_vote_info_dic[your_name].keys()
        not_done_uid_pairs = list(set(topic_uid_pair_dic[topic]) - set(all_uid_pair_done_list) - set(
            done_uid_pairs))  # 固定topic下，任何人都没做过的uid_pair
        done_n = len(done_uid_pairs)

    # uid_pair = not_done_uid_pairs[0]
    uid_pair = random.sample(not_done_uid_pairs, k=1)[0]
    return done_n + 1, example_dic[uid_pair], uid_pair


# --------------------------------------------------------
# 按钮变动
# --------------------------------------------------------


def your_name_submit(your_name, topic):
    done_n, example, uid_pair = get_one_example(your_name.strip(), topic)
    next_dialogue_text = f"next({done_n}/{len(example_dic_keys)})"
    history = get_chat_contents(example)

    if your_name not in time_consume_dic:
        time_consume_dic[your_name] = {}
    time_consume_dic[your_name][uid_pair] = {"start_time": datetime.datetime.now()}

    return history, next_dialogue_text, example['prompt'], uid_pair


def oppose_oppose_btn_click(approve_oppose):
    return f"submit{approve_oppose}"


def submit_click(submit_btn, uid_pair, your_name, comment_text, topic):
    topic = topic.split("(")[0]
    your_name = your_name.strip()
    if your_name == "":
        raise gr.Error('please input your name!')

    # 投票结果
    if submit_btn.replace("submit", "") == "👍":
        vote_value = 1
    elif submit_btn.replace("submit", "") == "👎":
        vote_value = -1
    else:
        raise gr.Error('please vote first!')

    if must_have_comment_text:
        if comment_text.strip() == "" or comment_text is None:
            raise gr.Error('comment can not be empty!')

    # 结果写入数据库
    if your_name not in all_user_vote_info_dic:
        all_user_vote_info_dic[your_name] = {}
    all_user_vote_info_dic[your_name][uid_pair] = {'topic': topic, "vote_value": vote_value, "comment": comment_text}

    # print_dic = {"name": your_name, "uid_pair": uid_pair, 'vote_value': vote_value, 'comment_text': comment_text}
    # opened_vote_log_f.write(f"########## submit-log: {json.dumps(print_dic)}\n")
    json.dump(all_user_vote_info_dic, open(save_vote_f, 'w'))
    # opened_vote_log_f.write(f"########## save-vote-f: {your_name} save vote f to: {save_vote_f}\n")

    return "vote done!"


def next_dialogue_btn_click(your_name, old_uid_pair, submit_text, comment_text, topic):
    topic = topic.split("(")[0]
    your_name = your_name.strip()

    if your_name is None or your_name == "":
        raise gr.Error('Must input your name')

    done_n, example, uid_pair = get_one_example(your_name, topic)
    next_dialogue_text = f"next({done_n}/{len(example_dic_keys)})"
    history = get_chat_contents(example)

    if your_name not in all_user_vote_info_dic or submit_text != "vote done!":
        raise gr.Error('results of last vote not submitted!')

    # 旧对话结束时间
    if your_name in time_consume_dic and old_uid_pair in time_consume_dic[your_name]:
        time_consume_dic[your_name][old_uid_pair]["end_time"] = datetime.datetime.now()
        if old_uid_pair not in all_user_vote_info_dic[your_name]:
            all_user_vote_info_dic[your_name][old_uid_pair] = {'topic': topic}
        all_user_vote_info_dic[your_name][old_uid_pair]['time_consume'] = round(
            (time_consume_dic[your_name][old_uid_pair]['end_time'] - time_consume_dic[your_name][old_uid_pair][
                'start_time']).seconds / 60, 2)  # 分钟来保存

        # 保存结束时间，用户统计
        print_dic = {"name": your_name,
                     "uid_pair": old_uid_pair,
                     'topic': topic,
                     'vote_value': all_user_vote_info_dic[your_name][old_uid_pair]['vote_value'],
                     "time_consume": all_user_vote_info_dic[your_name][old_uid_pair]['time_consume'],
                     'end_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                     'comment_text': comment_text,
                     }
        opened_vote_log_f.write(f"########## next-dialogue: {json.dumps(print_dic)}\n")

        json.dump(all_user_vote_info_dic, open(save_vote_f, 'w'))

        # 清空耗时字典
        for k in [kk for kk in time_consume_dic[your_name]]:
            del time_consume_dic[your_name][k]

    # 下一个对话开始时间
    if your_name not in time_consume_dic:
        time_consume_dic[your_name] = {}
    time_consume_dic[your_name][uid_pair] = {"start_time": datetime.datetime.now()}

    return history, next_dialogue_text, example['prompt'], uid_pair, "submit", "", ""


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------


topic_select_names = [f"{k}({len(topic_uid_pair_dic[k])})" for k in topic_uid_pair_dic.keys()]

if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# Dialogue quality scoring web")
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    your_name = gr.Textbox(label="your name", placeholder="Enter your name and press the enter key.",
                                           interactive=True)
                    topic = gr.Dropdown(choices=topic_select_names,
                                        value=topic_select_names[0],
                                        label="select a topic",
                                        interactive=True)
                uid_pair = gr.Textbox(label="uid_pair", interactive=False)
                background_text = gr.Textbox(lines=5, label="background", interactive=False)

                with gr.Row():
                    oppose_btn = gr.Button("👎")
                    approve_btn = gr.Button("👍")

                comment_text = gr.Textbox(label="comment", interactive=True)
                submit_btn = gr.Button("submit")
                submit_text = gr.Textbox(label="Commit status", interactive=False)

            with gr.Column():
                gr_chatbot = gr.Chatbot(label="Dialogue")
                next_dialogue = gr.Button(value="next")

        # analysis_table = gr.DataFrame(label="Evaluation results",
        #                               headers=['user name', "finish dialogues", "time_consume(hours)"],
        #                               value=get_analysis_result, every=2)
        your_name.submit(your_name_submit, [your_name, topic],
                         [gr_chatbot, next_dialogue, background_text, uid_pair],
                         queue=False)
        topic.change(your_name_submit, [your_name, topic],
                     [gr_chatbot, next_dialogue, background_text, uid_pair],
                     queue=False)
        approve_btn.click(oppose_oppose_btn_click, [approve_btn], [submit_btn])
        oppose_btn.click(oppose_oppose_btn_click, [oppose_btn], [submit_btn])
        submit_btn.click(submit_click, [submit_btn, uid_pair, your_name, comment_text, topic],
                         [submit_text])
        next_dialogue.click(next_dialogue_btn_click, [your_name, uid_pair, submit_text, comment_text, topic],
                            [gr_chatbot, next_dialogue, background_text, uid_pair, submit_btn, comment_text,
                             submit_text],
                            queue=False)

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9701)
