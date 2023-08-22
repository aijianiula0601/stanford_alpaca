import os
import sys
import json
import random
import gradio as gr

# -----------------------------------------------------------------------------------
# 暂时json给用户
# -----------------------------------------------------------------------------------

ROLE_A_NAME = "Jack"
ROLE_B_NAME = "Alice"


# --------------------------------------------------------
# 模型选择
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


def clear_f():
    return None, None


# --------------------------------------------------------
# 加载数据
# --------------------------------------------------------
data_f = "/Users/jiahong/Downloads/gpt4to_colloquial.txt"

example_dic = {}
with open(data_f) as fr:
    for line in fr:
        example = json.loads(line)
        k = example['uid_pair']
        assert k not in example_dic, f"error key:{k}"
        example_dic[k] = example

example_dic_keys = [k for k in example_dic.keys()]

# 所有用户信息
"""
{
    "name":{"uid_pair":-1|1,...,}
}
"""
all_user_name_info_dic = {}


def get_one_example(your_name):
    if your_name not in all_user_name_info_dic:
        done_n = 0
        not_done_uid_pairs = example_dic_keys
    else:
        done_uid_pairs = all_user_name_info_dic[your_name].keys()
        not_done_uid_pairs = list(set(example_dic_keys) - set(done_uid_pairs))
        done_n = len(done_uid_pairs)

    uid_pair = random.sample(not_done_uid_pairs, k=1)[0]
    return done_n, example_dic[uid_pair], uid_pair


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


def submit_click(submit_btn, uid_pair, your_name):
    # 投票结果
    vote_value = None
    if submit_btn.replace("submit", "") == "👍":
        vote_value = 1
    elif submit_btn.replace("submit", "") == "👎":
        vote_value = -1
    else:
        raise gr.Error('Must vote first!')

    # 结果写入数据库
    if your_name not in all_user_name_info_dic:
        all_user_name_info_dic[your_name] = {}
    all_user_name_info_dic[your_name][uid_pair] = vote_value
    print(f"##### your name:{your_name},uid_pair:{uid_pair},vote_value:{vote_value}")

    return "vote done!"


def next_dialogue_btn_click(your_name):
    if your_name is None or your_name == "":
        raise gr.Error('Must input your name')

    done_n, example, uid_pair = get_one_example(your_name)
    next_dialogue_text = f"next({done_n}/{len(example_dic_keys)})"

    history = get_history(example)

    return history, next_dialogue_text, example['prompt'], uid_pair, "submit", ""


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
                    approve_btn = gr.Button("👍")
                    oppose_btn = gr.Button("👎")

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
        submit_btn.click(submit_click, [submit_btn], [submit_text])
        next_dialogue.click(next_dialogue_btn_click, [your_name],
                            [gr_chatbot, next_dialogue, background_text, uid_pair, submit_btn, comment_text],
                            queue=False)

    # demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=9801)
