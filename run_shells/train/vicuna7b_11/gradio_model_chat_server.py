import os
import sys
import json
import gradio as gr

from gradio_model_self_chat_server import models_url_dic, get_message_list, models_list, mask_instruct, mask_instruct_v2

# -----------------------------------------------------------------------------------
# 跟two_persons_gpt35_llama.py的区别是：
# 在聊的时候，告诉模型它的人设是什么。让A模型生成的时候，模型A知道自己的人设，不知道提问者人设。
# 而跟two_persons_gpt35_llama在聊的时候是告诉模型，提问者的人设是什么。
# -----------------------------------------------------------------------------------

ROLE_A_NAME = "Jack"
ROLE_B_NAME = "Alice"


# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------


def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}:").strip())
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}:").strip())

    return rh


def role_b_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name, role_b_model_name,
                select_role_b):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_message_list = get_message_list(background=background_b,
                                           history=get_history(role_a_name, role_b_name, history))
    print("=" * 100)
    role_b_question = mask_instruct(role_b_message_list,
                                    role_dict={"user": role_a_name,
                                               "assistant": role_b_name},
                                    temperature=selected_temp, model_server_url=models_url_dic[role_b_model_name],
                                    select_role_b=select_role_b)

    print(f"{role_b_name}({role_b_model_name}): ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    return '', history


def toggle(user_message, selected_temp, chatbot, background_b, role_a_name, role_b_name, role_b_model_name,
           select_role_b):
    user_message, history = role_b_chat(selected_temp, user_message, chatbot, background_b, role_a_name,
                                        role_b_name, role_b_model_name, select_role_b)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f():
    return None, None


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------

prepared_role_b_dic = json.load(open("prompt_data.json"))
prepared_role_b_dic["None"] = {"role_name": "Ai", "background": "", "examples": ""}
prepared_role_b_dic[""] = {"role_name": "Ai", "background": "", "examples": ""}
role_b_list = list(prepared_role_b_dic.keys())


def update_select_role_b(role_b_key, user_name, select_role_b_model):
    if user_name.strip().lower() == prepared_role_b_dic[role_b_key]["role_name"].strip().lower():
        user_name = ROLE_B_NAME

    background_b = prepared_role_b_dic[role_b_key]["background"].format_map(
        {"role_a": user_name,
         "role_b": prepared_role_b_dic[role_b_key]["role_name"]})

    if select_role_b_model == "vicuna7b_ft_v15_v5_v2(优化后模型v3)":
        background_b += f" {prepared_role_b_dic[role_b_key]['role_name']} always answer in a colloquial way."

    examples_b = prepared_role_b_dic[role_b_key]["examples"].format_map(
        {"role_a": user_name,
         "role_b": prepared_role_b_dic[role_b_key]["role_name"]})

    input_prompt_b = f"{background_b}\n{examples_b}\n"

    return prepared_role_b_dic[role_b_key]["role_name"], input_prompt_b, user_name, None, None


def update_select_model():
    return None, None


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------
if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# LLM模型对话demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                          interactive=True)
                with gr.Row():
                    select_role_b_model = gr.Dropdown(choices=models_list, value=models_list[0],
                                                      label="选择角色B的模型",
                                                      interactive=True)
                with gr.Row():
                    select_role_b = gr.Dropdown(choices=role_b_list, value="None", label="请选择bot角色",
                                                interactive=True)

                with gr.Row():
                    user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="Human名字",
                                           value=ROLE_A_NAME, interactive=True)
                    bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="bot名字",
                                          value=ROLE_B_NAME, interactive=True)
                background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="bot角色背景")
                role_a_question = gr.Textbox(label="Human的问题", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="聊天记录")
                clear = gr.Button("清空聊天记录")

        user_name.change(update_select_role_b, [select_role_b, user_name, select_role_b_model],
                         [bot_name, background_role_b, user_name, gr_chatbot, role_a_question])
        bot_name.change(update_select_role_b, [select_role_b, user_name, select_role_b_model],
                        [bot_name, background_role_b, user_name, gr_chatbot, role_a_question])
        select_role_b_model.change(update_select_model, None, [gr_chatbot, role_a_question], queue=False)
        select_role_b.change(update_select_role_b, [select_role_b, user_name, select_role_b_model],
                             [bot_name, background_role_b, user_name, gr_chatbot, role_a_question])

        select_role_b_model.change(update_select_role_b, [select_role_b, user_name, select_role_b_model],
                                   [bot_name, background_role_b, user_name, gr_chatbot, role_a_question])

        clear.click(clear_f, None, [gr_chatbot, role_a_question])

        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b,
                                       user_name,
                                       bot_name, select_role_b_model, select_role_b],
                               outputs=[role_a_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8904, debug=True)
