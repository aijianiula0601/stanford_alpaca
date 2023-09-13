import os
import sys
import json
import requests
import gradio as gr

from gpt35_demo import *
import prompt_config


# pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(pjd)
#
# from web.bigolive_onlive.gpt35_demo import *

# -----------------------------------------------------------------------------------
# 模型线上gpt3.5的聊天
# -----------------------------------------------------------------------------------


def mask_instruct(message_list, temperature):
    """
    message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容
    """

    print("-" * 100)
    print("message_list:", message_list)
    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=temperature,
        messages=message_list
    )
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


def get_input_api_data(background, history=[], history_limit_turns=3):
    data_list = [{'role': 'system', 'content': background}]

    for i, h in enumerate(history[-(history_limit_turns * 2 + 1):]):
        if i % 2 == 0:
            data_list.append({"role": 'user', "content": h})
        else:
            data_list.append({'role': 'assistant', 'content': h})

    return data_list


def role_b_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name, history_turn_n):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_input_api_data = get_input_api_data(background=background_b,
                                               history=get_history(role_a_name, role_b_name, history),
                                               history_limit_turns=history_turn_n)

    role_b_question = mask_instruct(role_b_input_api_data,
                                    temperature=selected_temp)

    print(f"{role_b_name}: ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    return '', history


def toggle(user_message, selected_temp, chatbot, background_b, role_a_name, role_b_name, history_turn_n):
    user_message, history = role_b_chat(selected_temp, user_message, chatbot, background_b, role_a_name,
                                        role_b_name, history_turn_n)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f():
    return None, None


def update_select_model():
    return None, None


def bot_name_change(bot_name):
    if bot_name not in prompt_config.PERSONA_DICT:
        raise gr.Error(f"bot_name:{bot_name} no exist!")

    return prompt_config.PERSONA_DICT[bot_name]['background']


default_role_name = "Angelie_online"

# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# bigolive online test demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.7, label="Temperature", interactive=True)
                history_turn_n = gr.Slider(1, 10, step=1, value=1, label="remain history turns", interactive=True)

                with gr.Row():
                    user_name = gr.Textbox(lines=1, label="name of human", interactive=False, value='user')
                    bot_name = gr.Dropdown(value=default_role_name, choices=list(prompt_config.PERSONA_DICT.keys()),
                                           label="gpt引擎选择",
                                           interactive=True)

                background_role_b = gr.Textbox(lines=5,
                                               value=prompt_config.PERSONA_DICT[default_role_name]['background'],
                                               label="background of bot",
                                               interactive=False)
                role_a_question = gr.Textbox(placeholder="input your question and Press Enter to send.",
                                             label="question", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="chat bot")
                clear = gr.Button("clear history")

        clear.click(clear_f, None, [gr_chatbot, role_a_question])
        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b, user_name,
                                       bot_name, history_turn_n],
                               outputs=[role_a_question, gr_chatbot])

        bot_name.change(bot_name_change, [bot_name], [background_role_b])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8906, debug=True)
