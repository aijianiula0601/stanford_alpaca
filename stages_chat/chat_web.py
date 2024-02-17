import gradio as gr
import json
import random
import logging
import importlib

from aichat import PersonalInfo, AiChat
from utils import get_latest_history, get_history_str

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


def chat_f(history_list: list,
           living_on: bool,
           pic_to_ckb: bool,
           social_account_to_ckb: bool,
           user_question: str,
           role_name: str,
           user_language: str,
           previous_chat_history_summary_content: str):
    global ai_chat_obj
    if role_name != ai_chat_obj.role_name:
        ai_chat_obj = AiChat(role_data_dic=global_role_data_dic.get_role_data(role_name), gpt_version='gpt3.5')

    ai_chat_obj.ask_picture_change_to = pic_to_ckb
    ai_chat_obj.ask_social_account_change_to = social_account_to_ckb

    history_list[-1][-1] = f"user: {user_question}"

    summary_history_str, latest_history = get_latest_history(history_list, limit_turn_n=5)

    if summary_history_str:
        ai_chat_obj.previous_chat_summary = ai_chat_obj.summary_history(summary_history_str, previous_chat_history_summary_content)

    print(f"---round_i:{len(history_list)}")
    gpt_res, robot_answer = ai_chat_obj.stages_chat(round_i=len(history_list),
                                                    living_on=living_on,
                                                    latest_history=latest_history,
                                                    current_user_response=user_question,
                                                    language=user_language)
    history_list.append([f"{role_name}: {robot_answer}", None])

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
            with gr.Row():
                pic_to_ckb = gr.Dropdown(label='要照片是否引流到直播间', choices=['live', 'picture', None], value=None, interactive=True)
                social_account_to_ckb = gr.Dropdown(label='要社交账号是否引流到直播间', choices=['live', None], value=None, interactive=True)
            living_on_ckb = gr.Checkbox(label='是否在播', value=False, interactive=True)

            chat_analysis_tt = gr.Textbox(lines=3, value=None, label="chat_analysis", interactive=False)
            history_summary_tt = gr.Textbox(lines=3, value=None, label="历史记忆", interactive=False)

        with gr.Column():
            with gr.Row():
                clear_bt = gr.Button("clean history")
                another_day_bt = gr.Button("Another day")

            chat_bot_cb = gr.Chatbot(label="history", value=[[f"{role_robot_dd.value}: {sample_greeting_sentence}", None]], height=600)
            user_input_tt = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input_tt.submit(chat_f,
                         [chat_bot_cb, living_on_ckb, pic_to_ckb, social_account_to_ckb, user_input_tt, role_robot_dd, user_language_dd, history_summary_tt],
                         [chat_bot_cb, history_summary_tt, chat_analysis_tt, user_input_tt],
                         queue=False)
    clear_bt.click(clear_all, [], [chat_bot_cb, user_input_tt, chat_analysis_tt, history_summary_tt])
demo.queue().launch(server_name="0.0.0.0", server_port=8909)
