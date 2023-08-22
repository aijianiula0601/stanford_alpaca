import os
import sys
import json
import random
import gradio as gr

# --------------------------------------------------------
# 全局变量
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

all_user_vote_info_dic = {}
# 数据
data_f = "/Users/jiahong/Downloads/gpt4to_colloquial.txt"

# 投票结果保存路径
save_vote_f = "/Users/jiahong/Downloads/vote_res.txt"
opened_vot_f = open(save_vote_f, 'w', buffering=1)


# --------------------------------------------------------
# 获取聊天
# --------------------------------------------------------

def get_history(example: dict):
    human_name = example['human_name']
    bot_name = example['bot_name']

    history = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        question = f"{human_name}: {qa['question']}"
        answer = f"{bot_name}: {qa['answer']}"
        history.append([question, answer])

    return history


# --------------------------------------------------------
# 加载数据
# --------------------------------------------------------

example_dic = {}
with open(data_f) as fr:
    for line in fr:
        example = json.loads(line)
        k = example['uid_pair']
        assert k not in example_dic, f"error key:{k}"
        example_dic[k] = example

example_dic_keys = [k for k in example_dic.keys()]


def get_one_example(your_name):
    if your_name not in all_user_vote_info_dic:
        done_n = 0
        not_done_uid_pairs = example_dic_keys
    else:
        done_uid_pairs = all_user_vote_info_dic[your_name].keys()
        not_done_uid_pairs = list(set(example_dic_keys) - set(done_uid_pairs))
        done_n = len(done_uid_pairs)

    uid_pair = random.sample(not_done_uid_pairs, k=1)[0]
    return done_n + 1, example_dic[uid_pair], uid_pair


# --------------------------------------------------------
# 按钮变动
# --------------------------------------------------------


def your_name_change(your_name):
    done_n, example, uid_pair = get_one_example(your_name)
    next_dialogue_text = f"next({done_n}/{len(example_dic_keys)})"

    history = get_history(example)

    return history, next_dialogue_text, example['prompt'], uid_pair


def oppose_oppose_btn_click(approve_oppose):
    return f"submit{approve_oppose}"


def submit_click(submit_btn, uid_pair, your_name, comment_text):
    # 投票结果
    if submit_btn.replace("submit", "") == "👍":
        vote_value = 1
    elif submit_btn.replace("submit", "") == "👎":
        vote_value = -1
    else:
        raise gr.Error('please vote first!')

    if comment_text.strip() == "" or comment_text is None:
        raise gr.Error('comment can not be empty!')

    # 结果写入数据库
    if your_name not in all_user_vote_info_dic:
        all_user_vote_info_dic[your_name] = {}
    all_user_vote_info_dic[your_name][uid_pair] = {"vote_value": vote_value, "comment": comment_text}

    print_dic = {"name": your_name, "uid_pair": uid_pair, 'vote_value': vote_value, 'comment_text': comment_text}
    print(f"#####submit-log#####{json.dumps(print_dic)}")
    opened_vot_f.write(f"{json.dumps(print_dic)}\n")

    return "vote done!"


def next_dialogue_btn_click(your_name):
    if your_name is None or your_name == "":
        raise gr.Error('Must input your name')

    done_n, example, uid_pair = get_one_example(your_name)
    next_dialogue_text = f"next({done_n}/{len(example_dic_keys)})"
    history = get_history(example)

    return history, next_dialogue_text, example['prompt'], uid_pair, "submit", "", ""


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# Dialogue quality scoring web")
        with gr.Row():
            with gr.Column():
                your_name = gr.Textbox(label="your name", placeholder="please input your name", interactive=True)
                uid_pair = gr.Textbox(label="uid_pair", placeholder="uid_pair", interactive=False)
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

        your_name.change(your_name_change, [your_name], [gr_chatbot, next_dialogue, background_text, uid_pair],
                         queue=False)
        approve_btn.click(oppose_oppose_btn_click, [approve_btn], [submit_btn])
        oppose_btn.click(oppose_oppose_btn_click, [oppose_btn], [submit_btn])
        submit_btn.click(submit_click, [submit_btn, uid_pair, your_name, comment_text], [submit_text])
        next_dialogue.click(next_dialogue_btn_click, [your_name],
                            [gr_chatbot, next_dialogue, background_text, uid_pair, submit_btn, comment_text,
                             submit_text],
                            queue=False)

    # demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9801)
