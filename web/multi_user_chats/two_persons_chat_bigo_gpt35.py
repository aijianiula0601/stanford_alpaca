import os
import sys

import gradio as gr
import random

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

from two_bigo_gpt35 import *

ROLE_A_NAME = "Human"
ROLE_B_NAME = "Ai"
ROLE_A_START_QUESTION = "hi"


def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}: "))
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}: "))

    return rh


def role_ab_chat(user_message, history, background_a, background_b, role_a_name, role_b_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]
    role_b_input_api_data = get_input_api_data(background=get_background(background_a, role_b_name, role_a_name),
                                               history=get_history(role_a_name, role_b_name, history))
    role_b_question = chat_with_chatgpt(role_b_input_api_data)
    print(f"{role_b_name}: ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    # -------------------
    # role_a回答
    # -------------------
    role_a_input_api_data = get_input_api_data(background=get_background(background_b, role_a_name, role_b_name),
                                               history=get_history(role_a_name, role_b_name, history)[1:])
    role_a_question = chat_with_chatgpt(role_a_input_api_data)
    print(f"{role_a_name}: ", role_a_question)

    return role_a_question, history


def toggle(user_message, chatbot, background_a, background_b, role_a_name, role_b_name):
    user_message, history = role_ab_chat(user_message, chatbot, background_a, background_b, role_a_name, role_b_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# gpt3.5两个接口互相调用demo")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.5, label="Temperature超参,调的越小越容易输出常见字",
                                      interactive=True)
            with gr.Row():
                user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="roleA名字",
                                       value=ROLE_A_NAME, interactive=True)
                bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="roleB名字",
                                      value=ROLE_B_NAME, interactive=True)
            background_role_a = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleA背景")
            background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleB背景")
            role_a_question = gr.Textbox(placeholder="输入RoleA首次提出的问题",
                                         value=ROLE_A_START_QUESTION + "," + bot_name.value, label="roleA问题",
                                         interactive=True)

        with gr.Column():
            btn = gr.Button("点击生成一轮对话")
            gr_chatbot = gr.Chatbot(label="聊天记录")
            clear = gr.Button("清空聊天记录")

    btn.click(toggle, inputs=[role_a_question, gr_chatbot, background_role_a, background_role_b, user_name, bot_name],
              outputs=[role_a_question, gr_chatbot])

    clear.click(lambda: None, None, gr_chatbot)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=random.randint(8000, 9000))
