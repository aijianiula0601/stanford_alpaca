import os
import sys
import json
import gradio as gr
import random

from two_bigo_gpt35 import *
from llama_api_test import llama_respond

# ---------------------------------------------------
# 让A模型生成的时候，模型A知道提问者的人设，不知道自己的人设
# ---------------------------------------------------

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


def role_ab_chat(selected_temp, user_message, history, background_a, background_b, role_a_name, role_b_name,
                 role_a_model_name, role_b_model_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]
    role_b_input_api_data = get_input_api_data(background=get_background(background_a, role_b_name, role_a_name),
                                               history=get_history(role_a_name, role_b_name, history))
    print("----role_b_input_api_data:", role_b_input_api_data)
    if role_b_model_name == "gpt3.5":
        role_b_question = chat_with_chatgpt(role_b_input_api_data, selected_temp)
    elif role_b_model_name == "llama":
        role_b_question = llama_respond(role_b_input_api_data,
                                        role_dict={"user": role_a_name, "assistant": role_b_name},
                                        temperature=selected_temp)
        # print("---role_dic:", {"user": role_a_name, "assistant": role_b_name})
    else:
        raise Exception("-----Error选择的模型不存在！！！！")

    print(f"{role_b_name}({role_b_model_name}): ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    # -------------------
    # role_a回答
    # -------------------
    role_a_input_api_data = get_input_api_data(background=get_background(background_b, role_a_name, role_b_name),
                                               history=get_history(role_a_name, role_b_name, history)[1:])
    print("----role_a_input_api_data:", role_a_input_api_data)

    if role_a_model_name == "gpt3.5":
        role_a_question = chat_with_chatgpt(role_a_input_api_data, selected_temp)
    elif role_a_model_name == "llama":
        role_a_question = llama_respond(role_a_input_api_data,
                                        role_dict={"user": role_b_name, "assistant": role_a_name},
                                        temperature=selected_temp)
        # print("---role_dic:", {"user": role_b_name, "assistant": role_a_name})

    else:
        raise Exception("-----Error选择的模型不存在！！！！")

    print(f"{role_a_name}({role_a_model_name}): ", role_a_question)
    return role_a_question, history


def toggle(user_message, selected_temp, chatbot, background_a, background_b, role_a_name, role_b_name,
           role_a_model_name, role_b_model_name):
    user_message, history = role_ab_chat(selected_temp, user_message, chatbot, background_a, background_b, role_a_name,
                                         role_b_name, role_a_model_name, role_b_model_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f(bot_name):
    return None, ROLE_A_START_QUESTION + ", " + bot_name + "!"


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------
prepared_role_a_dic = json.load(open("prepared_background.json"))
prepared_role_a_dic["None"] = {"role_name": "Human", "background": ""}
prepared_role_a_dic[""] = {"role_name": "Human", "background": ""}
role_a_list = list(prepared_role_a_dic.keys())
prepared_role_b_dic = json.load(open("prepared_background.json"))
prepared_role_b_dic["None"] = {"role_name": "Ai", "background": ""}
prepared_role_b_dic[""] = {"role_name": "Ai", "background": ""}
role_b_list = list(prepared_role_b_dic.keys())


def update_select_role_a(role_key, bot_name):
    return prepared_role_a_dic[role_key]["role_name"], \
           prepared_role_a_dic[role_key]["background"], \
           None, \
           ROLE_A_START_QUESTION + ", " + bot_name + "!"


def update_select_role_b(role_key, bot_name):
    return prepared_role_b_dic[role_key]["role_name"], \
           prepared_role_b_dic[role_key]["background"], \
           None, \
           ROLE_A_START_QUESTION + ", " + bot_name + "!"


def update_select_model(bot_name):
    return None, ROLE_A_START_QUESTION + ", " + bot_name + "!"


# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------
models_list = ["gpt3.5", "llama"]

# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# 两个LLM模型互相对话demo")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                      interactive=True)
            with gr.Row():
                select_role_a_model = gr.Dropdown(choices=models_list, value=models_list[0], label="选择角色A的模型",
                                                  interactive=True)
                select_role_b_model = gr.Dropdown(choices=models_list, value=models_list[0], label="选择角色B的模型",
                                                  interactive=True)
            with gr.Row():
                select_role_a = gr.Dropdown(choices=role_a_list, value="None", label="请选择一个角色A",
                                            interactive=True)
                select_role_b = gr.Dropdown(choices=role_b_list, value="None", label="请选择一个角色B",
                                            interactive=True)

            with gr.Row():
                user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="roleA名字",
                                       value=ROLE_A_NAME, interactive=True)
                bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="roleB名字",
                                      value=ROLE_B_NAME, interactive=True)
            background_role_a = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleA背景")
            background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleB背景")
            role_a_question = gr.Textbox(placeholder="输入RoleA首次提出的问题",
                                         value=ROLE_A_START_QUESTION + ", " + bot_name.value + '!', label="roleA问题",
                                         interactive=True)
        with gr.Column():
            btn = gr.Button("点击生成一轮对话")
            gr_chatbot = gr.Chatbot(label="聊天记录")
            clear = gr.Button("清空聊天记录")

    bot_name.change(lambda x: ROLE_A_START_QUESTION + ", " + x + "!", bot_name, role_a_question)
    select_role_a_model.change(update_select_model, [bot_name], [gr_chatbot, role_a_question], queue=False)
    select_role_b_model.change(update_select_model, [bot_name], [gr_chatbot, role_a_question], queue=False)
    select_role_a.change(update_select_role_a, [select_role_a, bot_name],
                         [user_name, background_role_a, gr_chatbot, role_a_question])
    select_role_b.change(update_select_role_b, [select_role_b, bot_name],
                         [bot_name, background_role_b, gr_chatbot, role_a_question])
    btn.click(toggle,
              inputs=[role_a_question, selected_temp, gr_chatbot, background_role_a, background_role_b, user_name,
                      bot_name, select_role_a_model, select_role_b_model],
              outputs=[role_a_question, gr_chatbot])

    clear.click(clear_f, [bot_name], [gr_chatbot, role_a_question])

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=8990)
# demo.launch(server_name="202.168.100.165", server_port=8990)
