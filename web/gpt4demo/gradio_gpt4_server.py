import os
import sys
import json
import requests
import gradio as gr

from gpt4demo import *

# -----------------------------------------------------------------------------------
# 跟two_persons_gpt35_llama.py的区别是：
# 在聊的时候，告诉模型它的人设是什么。让A模型生成的时候，模型A知道自己的人设，不知道提问者人设。
# 而跟two_persons_gpt35_llama在聊的时候是告诉模型，提问者的人设是什么。
# -----------------------------------------------------------------------------------

ROLE_A_NAME = "Jack"
ROLE_B_NAME = "Alice"


def mask_instruct(message_list, temperature):
    """
    message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容
    """

    print("-" * 100)
    print("message_list:", message_list)
    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        messages=message_list,
        temperature=temperature,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    print("response:", response)
    print("-" * 100)

    return response['choices'][0]['message']['content']


def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}:").strip())
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}:").strip())

    return rh


def get_input_api_data(background, history=[]):
    data_list = [{'role': 'system', 'content': background}]
    for i, h in enumerate(history):
        if i % 2 == 0:
            data_list.append({"role": 'user', "content": h})
        else:
            data_list.append({'role': 'assistant', 'content': h})

    return data_list


def role_b_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_input_api_data = get_input_api_data(background=background_b,
                                               history=get_history(role_a_name, role_b_name, history))
    role_b_question = mask_instruct(role_b_input_api_data,
                                    temperature=selected_temp)

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


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------


def update_select_model():
    return None, None


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# gpt4体验demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.7, label="Temperature超参,调的越小越容易输出常见字",
                                          interactive=True)

                with gr.Row():
                    user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="Human名字",
                                           value=ROLE_A_NAME, interactive=True)
                    bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="bot名字",
                                          value=None, interactive=True)
                background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="bot角色背景")
                role_a_question = gr.Textbox(placeholder="输入问题", label="问题", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="聊天记录")
                clear = gr.Button("清空聊天记录")

        clear.click(clear_f, None, [gr_chatbot, role_a_question])
        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b, user_name,
                                       bot_name],
                               outputs=[role_a_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8905, debug=True)
