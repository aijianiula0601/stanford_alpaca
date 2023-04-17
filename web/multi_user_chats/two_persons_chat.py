import os
import sys
import gradio as gr

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

ROLE_A_NAME = "Human"
ROLE_B_NAME = "Ai"
ROLE_A_START_QUESTION = "hi"


def role_a(user_message, history, role_a=ROLE_A_NAME):
    human_invitation = role_a + ": "
    return "", history + [[human_invitation + user_message, None]], role_a


def role_b(history, temperature=1.0, background="", role_a=ROLE_A_NAME,
           role_b=ROLE_B_NAME):
    human_invitation = role_a + ": "
    ai_invitation = role_b + ": "

    return history, temperature, background, role_a, role_b


def toggle(button):
    if button == "Start":
        button = "Stop"
        print("Starting operation...")
    else:
        button = "Start"
        print("Stopping operation...")
    return button


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# gpt3.5两个接口互相调用demo")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.5, label="Temperature超参,调的越小越容易输出常见字",
                                      interactive=True)
            with gr.Row():
                user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="roleA名字",
                                       value=ROLE_A_NAME, interactive=True)
                bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="roleB名字",
                                      value=ROLE_B_NAME, interactive=True)
            background_role_a = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleA背景")
            background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleB背景")
            role_a_question = gr.Textbox(placeholder="输入RoleA首次提出的问题",
                                         value=ROLE_A_START_QUESTION + "," + user_name.value, label="roleA首问题",
                                         interactive=True)
            with gr.Row():
                btn = gr.Button("Start")

        with gr.Column():
            clear = gr.Button("清空聊天记录")

            chatbot = gr.Chatbot(label="聊天记录")

    btn.click(toggle, btn, btn)
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(server_name="0.0.0.0", server_port=8094)
