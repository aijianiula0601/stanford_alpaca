import os
import sys
import json
import gradio as gr
import random

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("----pdj:", pdj)
sys.path.append(pdj)

from bigo_anchor_gpt35_api import *
from web.multi_user_chats.llama_api_test import llama_respond

imageUrlList = {
    "主播NatySnow": "https://img.like.video/asia_live/4hd/0OZEWB.png", \
    "热爱旅行的年轻女企业家": "https://img.like.video/asia_live/4hd/0OZEWB.png", \
    "热爱瑜伽的女程序猿": "https://img.like.video/asia_live/4hd/2haspf.png", \
    "泰勒·斯威夫特 (Taylor Swift)": "https://img.like.video/asia_live/4hd/1F8SjP.png", \
    "色情女教师": "https://img.like.video/asia_live/4hd/02DuDs.png", \
    "16岁的傲慢女朋友": "https://img.like.video/asia_live/4hd/0DO5oW.png", \
    "手握实权的宰相": "https://img.like.video/asia_live/4hd/0IUBEd.png", \
    "霸道总裁": "https://img.like.video/asia_live/4hd/0DP6QW.png", \
    "外星人帅哥教授": "https://img.like.video/asia_live/4hd/2LEYAR.png"}


def role_anchor_user_chat(selected_temp, user_message, history, background_anchor, user_name, anchor_name,
                          role_anchor_model_name):
    # -------------------
    # 主播模型回答
    # -------------------
    if len(history) > 0:
        history[-1][
            1] = f"{user_name}: {user_message}" if user_message is not None else None and user_message.strip() != ""
    history = history + [[None, None]]

    role_b_input_api_data = get_input_api_data(get_background(background_anchor, anchor_name, user_name), user_name,
                                               anchor_name, history)
    print("----role_b_input_api_data:", role_b_input_api_data)

    if role_anchor_model_name == "gpt3.5":
        anchor_question = chat_with_chatgpt(role_b_input_api_data, selected_temp)
    elif role_anchor_model_name == "llama":
        anchor_question = llama_respond(role_b_input_api_data,
                                        role_dict={"user": user_name, "assistant": anchor_name},
                                        temperature=selected_temp)
    else:
        raise Exception("-----Error选择的模型不存在！！！！")

    print(f"{anchor_name}({role_anchor_model_name}): ", anchor_question)

    history[-1][0] = f"{anchor_name}: {anchor_question}"

    return history


def toggle(user_message, selected_temp, chatbot, background_anchor, user_name, anchor_name,
           role_anchor_model_name):
    history = role_anchor_user_chat(selected_temp, user_message, chatbot, background_anchor,
                                    user_name, anchor_name, role_anchor_model_name)

    print("-" * 100)
    return None, history


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------
prepared_anchor_dic = json.load(open("prepared_background.json"))
prepared_anchor_dic["None"] = {"role_name": "Ai", "background": ""}
prepared_anchor_dic[""] = {"role_name": "Ai", "background": ""}
anchor_name_list = list(prepared_anchor_dic.keys())


def update_select_role(role_key):
    return prepared_anchor_dic[role_key]["role_name"], \
           prepared_anchor_dic[role_key]["background"], \
           None


# --------------------------------------------------------
# 全局变量
# --------------------------------------------------------
models_list = ["gpt3.5", "llama"]

ROLE_HUMAN_NAME = "Jack"
ROLE_AI_NAME = anchor_name_list[0]
# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# LLM虚拟主播拉新")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                      interactive=True)
            with gr.Row():
                select_anchor_model = gr.Dropdown(choices=models_list, value=models_list[0], label="选择角色A的模型",
                                                  interactive=True)
            with gr.Row():
                image_fig = gr.Image(imageUrlList[ROLE_AI_NAME], label="虚拟人头像").style(height=128, width=128)
                select_anchor = gr.Dropdown(choices=anchor_name_list, value=ROLE_AI_NAME, label="选择一个主播",
                                            interactive=True)

            with gr.Row():
                anchor_name = gr.Textbox(lines=1, placeholder="设置主播名字， ...", label="主播名字",
                                         value=prepared_anchor_dic[ROLE_AI_NAME]['role_name'], interactive=True)
                user_name = gr.Textbox(lines=1, placeholder="设置用户名字， ...", label="用户名字",
                                       value=ROLE_HUMAN_NAME, interactive=True)
            background_anchor = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleA背景",
                                           value=prepared_anchor_dic[ROLE_AI_NAME]['background'])
            user_question = gr.Textbox(placeholder="用户的回答，由主播来主动提问。", label="用户的回答", interactive=True)
        with gr.Column():
            btn = gr.Button("点击生成一轮对话")
            gr_chatbot = gr.Chatbot(label="聊天记录")
            clear = gr.Button("清空聊天记录")

    select_anchor_model.change(lambda: None, None, gr_chatbot, queue=False)
    select_anchor.change(update_select_role, [select_anchor],
                         [anchor_name, background_anchor, gr_chatbot])
    btn.click(toggle,
              inputs=[user_question, selected_temp, gr_chatbot, background_anchor, user_name, anchor_name,
                      select_anchor_model],
              outputs=[user_question, gr_chatbot])

    user_question.submit(toggle,
                         inputs=[user_question, selected_temp, gr_chatbot, background_anchor, user_name, anchor_name,
                                 select_anchor_model],
                         outputs=[user_question, gr_chatbot])

    clear.click(lambda: None, None, gr_chatbot)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=random.randint(8000, 9000))
# demo.launch(server_name="202.168.100.165", server_port=8990)
