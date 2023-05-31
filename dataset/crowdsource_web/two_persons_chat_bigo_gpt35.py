import os
import sys
import json
import gradio as gr
import random

pdj_dir = os.path.dirname(os.path.abspath(__file__))
print(f"prj_dir:{pdj_dir}")

from two_bigo_gpt35 import *


# ----------------------------------------------------------------
# 说明：这个页面用于给标注人员设计prompt体验gpt3.5互聊的效果
# ----------------------------------------------------------------

def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}: "))
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}: "))
    return rh


def role_ab_chat(selected_temp, user_message, history, background_a, background_b, role_a_name, role_b_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]
    role_b_input_api_data = get_input_api_data(background=background_b,
                                               history=get_history(role_a_name, role_b_name, history))
    print("----role_b_input_api_data:", role_b_input_api_data)
    role_b_question = chat_with_chatgpt(role_b_input_api_data, selected_temp)
    print(f"{role_b_name}: ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    # -------------------
    # role_a回答
    # -------------------
    role_a_input_api_data = get_input_api_data(background=background_a,
                                               history=get_history(role_a_name, role_b_name, history)[1:])
    print("----role_a_input_api_data:", role_a_input_api_data)
    role_a_question = chat_with_chatgpt(role_a_input_api_data, selected_temp)
    print(f"{role_a_name}: ", role_a_question)

    return role_a_question, history


def toggle(user_message, selected_temp, chatbot, background_a, background_b, role_a_name, role_b_name):
    user_message, history = role_ab_chat(selected_temp, user_message, chatbot, background_a, background_b, role_a_name,
                                         role_b_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


default_save_dir = f"{pdj_dir}/save_records"
os.system(f"mkdir -p {default_save_dir}")


def save_record(save_name, chatbot, background_a, background_b, role_a_name, role_b_name):
    if save_name is None or len(
            chatbot) <= 0 or save_name.strip() == "" or "/" in save_name or "Failed to save file!" in save_name or "Saved to" in save_name or background_a == "" or background_b == "" or role_b_name == "" or role_a_name == "":
        return "Failed to save file! Please enter the file name!"

    file_path = f"{default_save_dir}/{save_name}.json"
    save_data_dic = {"background_a": background_a, "background_b": background_b, "role_a_name": role_a_name,
                     "role_b_name": role_b_name, "qas": chatbot}
    json.dump(save_data_dic, open(file_path, 'w'))
    return f"Saved to:{file_path}"


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# gpt3.5 self-chat demo")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.9,
                                      label="The parameter of temperature, The smaller the temperature is, the easier it is to output common words",
                                      interactive=True)

            with gr.Row():
                user_name = gr.Textbox(lines=1, placeholder="set the name for roleA", label="roleA's name",
                                       interactive=True)
                bot_name = gr.Textbox(lines=1, placeholder="set the name for roleB", label="roleB's name",
                                      interactive=True)
            background_role_a = gr.Textbox(lines=5, placeholder="set the background for roleA",
                                           label="roleA's background ")
            background_role_b = gr.Textbox(lines=5, placeholder="set the background for roleB",
                                           label="roleA's background ")
            role_a_question = gr.Textbox(placeholder="input the first question of roleA", label="question of roleA",
                                         interactive=True)

        with gr.Column():
            btn = gr.Button("Generate a turn")
            gr_chatbot = gr.Chatbot(label="Chat record")
            clear = gr.Button("Clear chat history")
            save_text = gr.Textbox(placeholder="Enter the file name to save the chat record", value=None,
                                   label="name of save file", interactive=True)
            save_chatbot = gr.Button("Save chat records")

    btn.click(toggle,
              inputs=[role_a_question, selected_temp, gr_chatbot, background_role_a, background_role_b, user_name,
                      bot_name],
              outputs=[role_a_question, gr_chatbot])

    save_chatbot.click(save_record,
                       inputs=[save_text, gr_chatbot, background_role_a, background_role_b, user_name, bot_name],
                       outputs=[save_text])

    clear.click(lambda x: [None, None, None], None, [gr_chatbot, role_a_question, save_text])

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=9010)
# demo.launch(server_name="202.168.100.178", server_port=8988)
