import os
import sys
import json
import requests
import gradio as gr

import prompt_config
from aichat import ChatObject

# pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(pjd)
#
# from web.bigolive_onlive.gpt35_demo import *

# -----------------------------------------------------------------------------------
# 模型线上gpt3.5的聊天
# -----------------------------------------------------------------------------------


ai_chat = ChatObject()


def get_history_str(history: list):
    if len(history) <= 0:
        return ''
    history_list = []
    for qa in history:
        for q_a in qa:
            if q_a is not None:
                history_list.append(q_a)
    return '\n'.join(history_list)


def get_latest_history(history: list, limit_turn_n: int):
    to_summary_history = []
    new_summary_flag = False
    if len(history) % limit_turn_n == 0 and len(history) // limit_turn_n > 1:
        if len(history) >= limit_turn_n * 2:
            new_summary_flag = True
            # 给过去做总结的历史
            to_summary_history = history[:-limit_turn_n][-limit_turn_n:]

    if new_summary_flag:
        latest_history = history[-limit_turn_n:]
    else:
        cur_turn_n = limit_turn_n + len(history) % limit_turn_n
        latest_history = history[-cur_turn_n:]

    return to_summary_history, latest_history


def chat_f(history: list,
           user_question: str,
           role_human: str = "user",
           role_robot: str = "robot",
           limit_turn_n: int = 5,
           gpt_version: str = 'gpt3.5',
           selected_temp: float = 0.7
           ):
    history.append([f"{role_human}: {user_question}", None])

    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)

    _, latest_history = get_latest_history(history[:-1], limit_turn_n)

    # ---------------------
    # 模型回复
    # ---------------------
    answer_text = ai_chat.question_response(latest_history=get_history_str(latest_history),
                                            current_user_question=user_question,
                                            selected_temp=selected_temp)

    print(f"answer:{answer_text}")
    print("*" * 50)
    print("new chat")
    print("*" * 50)

    history[-1][-1] = f"{role_robot}: {answer_text}"

    return history, None


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
                with gr.Row():
                    selected_temp = gr.Slider(0, 1, value=0.7, label="Temperature", interactive=True)
                    gpt_select = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                             interactive=True)

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
                user_question = gr.Textbox(placeholder="input your question and Press Enter to send.",
                                           label="question", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="chat bot")
                clear = gr.Button("clear history")

        clear.click(clear_f, None, [gr_chatbot, user_question])
        user_question.submit(chat_f,
                             inputs=[gr_chatbot, user_question, user_name, bot_name, history_turn_n, gpt_select,
                                     selected_temp],
                             outputs=[gr_chatbot, user_question])

        bot_name.change(bot_name_change, [bot_name], [background_role_b])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8906, debug=True)
