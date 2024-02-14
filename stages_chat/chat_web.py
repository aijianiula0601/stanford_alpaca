import gradio as gr
import json
import random
import logging
import importlib

from aichat import PersonalInfo, AiChat


# -----------------
# 辅助函数
# -----------------

def get_history_str(history: list):
    if len(history) <= 0:
        return None
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

    return get_history_str(to_summary_history), get_history_str(latest_history)


# -----------------
# 初始化人设信息
# -----------------
global_role_data_dic = PersonalInfo("data/roles.json")
default_role_name = 'rosa'
print(global_role_data_dic.role_data_dic)

# -----------------
# 初始化打招呼
# -----------------
greeting_file = "data/greeting.json"
greeting_data_list = json.load(open(greeting_file, 'r', encoding='utf-8'))['first_day']
sample_greeting_sentence = random.sample(greeting_data_list, k=1)[0]

# -----------------
# 聊天
# -----------------

ai_chat_obj = AiChat(role_data_dic=global_role_data_dic.get_role_data(default_role_name), gpt_version='gpt3.5')


def chat_f(history_list: list, user_question, role_robot, user_language):
    history_list[-1][-1] = f"user: {user_question}"

    summary_history_str, latest_history_str = get_latest_history(history_list, limit_turn_n=5)

    if summary_history_str:
        ai_chat_obj.previous_chat_summary = ai_chat_obj.summary_history(summary_history_str)

    print(f"---round_i:{len(history_list)}")
    gpt_res, robot_answer = ai_chat_obj.stages_chat(round_i=len(history_list),
                                                    latest_history_str=latest_history_str,
                                                    current_user_response=user_question,
                                                    language=user_language)
    history_list.append([f"{role_robot}: {robot_answer}", None])

    return history_list, summary_history_str, gpt_res, None


def clear_all():
    print("---clear all!!!")
    sample_greeting_sentence = random.sample(greeting_data_list, k=1)[0]
    chat_bot = [[f"{role_robot_dd.value}: {sample_greeting_sentence}", None]]

    return [chat_bot] + [None] * 3


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# stage chat聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                role_robot_dd = gr.Dropdown(value=default_role_name, choices=list(global_role_data_dic.role_data_dic.keys()), label="角色选择", interactive=True)
                user_language_dd = gr.Dropdown(value='English', choices=['English', 'Chinese', 'Spanish', 'Bengali', 'Arabic'], label="语言选择", interactive=True)
                gpt_version_dd = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt版本", interactive=True)

            chat_analysis_tt = gr.Textbox(lines=3, value=None, label="chat_analysis", interactive=False)
            history_summary_tt = gr.Textbox(lines=3, value=None, label="历史记忆", interactive=False)

        with gr.Column():
            with gr.Row():
                clear_bt = gr.Button("clean history")
                another_day_bt = gr.Button("Another day")

            chat_bot_cb = gr.Chatbot(label="history", value=[[f"{role_robot_dd.value}: {sample_greeting_sentence}", None]], height=600)
            user_input_tt = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input_tt.submit(chat_f,
                         [chat_bot_cb, user_input_tt, role_robot_dd, user_language_dd],
                         [chat_bot_cb, history_summary_tt, chat_analysis_tt, user_input_tt],
                         queue=False)
    clear_bt.click(clear_all, [], [chat_bot_cb, user_input_tt, chat_analysis_tt, history_summary_tt])
demo.queue().launch(server_name="0.0.0.0", server_port=8909)
