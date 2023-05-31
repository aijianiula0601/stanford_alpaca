import os
import sys
import json
import gradio as gr
import random

pdj_dir = os.path.dirname(os.path.abspath(__file__))
print(f"prj_dir:{pdj_dir}")

from two_bigo_gpt35 import *


# ----------------------------------------------------------------
# 说明：这个页面用于给标注人员设计prompt体验人机对话效果
# ----------------------------------------------------------------

def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}: "))
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}: "))
    return rh


def role_ab_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name):
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

    return None, history


def toggle(user_message, selected_temp, chatbot, background_b, role_a_name, role_b_name):
    user_message, history = role_ab_chat(selected_temp, user_message, chatbot, background_b, role_a_name,
                                         role_b_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


default_save_dir = f"{pdj_dir}/save_records"
os.system(f"mkdir -p {default_save_dir}")


def save_record(save_name, chatbot, background_b, role_a_name, role_b_name):
    if save_name is None or len(
            chatbot) <= 0 or save_name.strip() == "" or "/" in save_name or "Failed to save file!" in save_name or "Saved to" in save_name or background_b == "" or role_b_name == "" or role_a_name == "" or "please enter other same!" in save_name:
        return "Failed to save file! Please enter the file name!"

    file_path = f"{default_save_dir}/{save_name}.json"

    if os.path.exists(file_path):
        return f"The name of {save_name} used, please enter other same!"

    save_data_dic = {"background_b": background_b, "human": role_a_name,
                     "bot": role_b_name, "qas": chatbot}
    json.dump(save_data_dic, open(file_path, 'w'))
    return f"Saved to:{file_path}"


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# gpt3.5 human-bot-chat demo")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.9,
                                      label="The parameter of temperature, The smaller the temperature is, the easier it is to output common words",
                                      interactive=True)

            with gr.Row():
                user_name = gr.Textbox(lines=1, placeholder="set the name for human", label="Human",
                                       interactive=True)
                bot_name = gr.Textbox(lines=1, placeholder="set the name for bot", label="Bot",
                                      interactive=True)
            background_role_b = gr.Textbox(lines=5, placeholder="set the background for bot",
                                           label="bot's background ")
            role_a_question = gr.Textbox(placeholder="Input the question, enter to send!", label="question of human",
                                         interactive=True)

        with gr.Column():
            gr_chatbot = gr.Chatbot(label="Chat record")
            clear = gr.Button("Clear chat history")
            save_text = gr.Textbox(placeholder="Enter the file name to save the chat record", value=None,
                                   label="name of save file", interactive=True)
            save_chatbot = gr.Button("Save chat records")

    role_a_question.submit(toggle,
                           inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b, user_name,
                                   bot_name],
                           outputs=[role_a_question, gr_chatbot])

    save_chatbot.click(save_record,
                       inputs=[save_text, gr_chatbot, background_role_b, user_name, bot_name],
                       outputs=[save_text])

    clear.click(lambda x: [None, None, None], None, [gr_chatbot, role_a_question, save_text])

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=9011)
# demo.launch(server_name="202.168.100.178", server_port=8988)
