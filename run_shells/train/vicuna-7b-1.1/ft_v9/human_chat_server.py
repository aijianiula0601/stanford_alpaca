import os
import sys
import json
import gradio as gr
import requests
import copy

# pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# print("pdj:", pdj)
# sys.path.append(pdj)

from self_chat_server import *

# -----------------------------------------------------------------------------------
# 跟two_persons_gpt35_llama.py的区别是：
# 在聊的时候，告诉模型它的人设是什么。让A模型生成的时候，模型A知道自己的人设，不知道提问者人设。
# 而跟two_persons_gpt35_llama在聊的时候是告诉模型，提问者的人设是什么。
# -----------------------------------------------------------------------------------

ROLE_A_NAME = "Human"
ROLE_B_NAME = "Ai"
ROLE_A_START_QUESTION = "hi"

# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------


server_url = "http://202.168.114.102:6029/api"

PROMPT_DICT = {
    "conversation": ("{background}\n"
                     "The following is a conversation between {human_name} and {bot_name}.\n\n"),
    "None": ""
}


def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}: "))
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}: "))

    return rh


def role_b_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_input_api_data = get_input_api_data(background=background_b,
                                               history=get_history(role_a_name, role_b_name, history))

    role_b_question = mask_instruct(role_b_input_api_data,
                                    role_dict={"user": role_a_name,
                                               "assistant": role_b_name},
                                    temperature=selected_temp, model_server_url=server_url)

    print(f"{role_b_name}: ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    return '', history


def toggle(user_message, selected_temp, chatbot, background_b, role_a_name, role_b_name):
    user_message, history = role_b_chat(selected_temp, user_message, chatbot, background_b, role_a_name,
                                        role_b_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f():
    return None, None


def update_select_model():
    return None, None


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# LLM模型对话demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                          interactive=True)
                with gr.Row():
                    user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="Human名字",
                                           value=ROLE_A_NAME, interactive=True)
                    bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="bot名字",
                                          value=ROLE_B_NAME, interactive=True)
                background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="bot角色背景")
                role_a_question = gr.Textbox(placeholder="输入问题", label="问题", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="聊天记录")
                clear = gr.Button("清空聊天记录")

        clear.click(clear_f, None, [gr_chatbot, role_a_question])

        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b,
                                       user_name,
                                       bot_name],
                               outputs=[role_a_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8993, debug=True)
