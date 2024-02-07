import gradio as gr
import json
import random
import logging
import importlib

from aichat import PersonalInfo, AiChat

# -----------------
# 初始化人设信息
# -----------------
global_role_data_dic = PersonalInfo("data/roles.json")
default_role_name = 'rosa'
print(global_role_data_dic.role_data_dic)

# -----------------
# 聊天
# -----------------






with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# stage chat聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                role_robot = gr.Dropdown(value=default_role_name, choices=list(global_role_data_dic.role_data_dic.keys()), label="角色选择", interactive=True)
                user_language_code = gr.Dropdown(value='Chinese', choices=['English', 'Chinese', 'Spanish', 'Bengali', 'Arabic'], label="语言选择", interactive=True)
                gpt_version = gr.Dropdown(value='3.5', choices=['3.5', 'gpt4'], label="gpt版本", interactive=True)

            machine_state = gr.Textbox(lines=1, value=None, label="内在状态", interactive=True)
            chat_analysis = gr.Textbox(lines=3, value=None, label="chat_analysis", interactive=False)
            history_summary = gr.Textbox(lines=3, value=None, label="历史记忆", interactive=False)

        with gr.Column():
            with gr.Row():
                clear = gr.Button("clean history")
                another_day = gr.Button("Another day")

            chat_bot = gr.Chatbot(label="history", value=None, height=600)
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

demo.queue().launch(server_name="0.0.0.0", server_port=8088)
