import os
import sys
import threading

import gradio as gr
import time
import random

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

ROLE_A_NAME = "Human"
ROLE_B_NAME = "Ai"
ROLE_A_START_QUESTION = "hi"

global_i = 0


def role_a_chat(user_message, history):
    return user_message + f"{global_i}", history + [[user_message + f"{global_i}", None]]


def role_b_chat(history):
    global global_i
    bot_message = random.choice(["Yes", "No"]) + f"{global_i}"
    global_i += 1
    history[-1][1] = bot_message

    return history


click_state = "start"


def toggle(user_message, chatbot):
    global click_state
    if click_state == "start":
        user_message, history = role_a_chat(user_message, chatbot)
        history = role_b_chat(history)
        chatbot += history[len(chatbot):]
        return chatbot
    else:
        return chatbot


def stop_click(btn):
    global click_state

    if btn == "Start":
        btn = "Stop"
        click_state = "stop"
    else:
        btn = "Start"
        click_state = "start"

    return btn


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
                                         value=ROLE_A_START_QUESTION + "," + user_name.value, label="roleA首问题",
                                         interactive=True)
            with gr.Row():
                start_btn = gr.Button("Start")
                stop_btn = gr.Button("Start")

        with gr.Column():
            clear = gr.Button("清空聊天记录")
            gr_chatbot = gr.Chatbot(label="聊天记录")

    start_btn.click(toggle, [role_a_question, gr_chatbot], gr_chatbot, every=2, queue=True)
    stop_btn.click(stop_click, inputs=[stop_btn], outputs=[stop_btn])
    clear.click(lambda: None, None, gr_chatbot)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=random.randint(8000, 9000))
