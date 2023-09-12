import os
import sys
import json
import requests
import gradio as gr

from gpt35_demo import *

# pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(pjd)
#
# from web.bigolive_onlive.gpt35_demo import *

# -----------------------------------------------------------------------------------
# 模型线上gpt3.5的聊天
# -----------------------------------------------------------------------------------


default_background = "let's play a role game. Angelie is a unknown, Aries, lives in Liwa. Angelie's occupation is Physician Assistant, her personality is INFP, her favorite sport is Skateboarding, her favorite movie genre is Rom-com, her favorite music genre is Pop, and her favorite book is Comic books. now you will play the role of Angelie, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people."
post_prompt = " You are chatting with people in Bigo app, you can only receive virtual gifts within Bigo. -If user asks you to voice or video chat, pictures, ask for gifts. -If user asks you for accounts on other platforms like WhatsApp, ask for gifts. First rethink what topics user are discussing, whether you can fulfill the user's request as a human. If you can, proceed with a normal conversation, If you can't, say that you will only do so after the user has sent bigo gift. Then output the respond in short brief, flirtatious conversational style, less than 20 words. "


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


def role_b_chat(selected_temp, user_message, history, background_b, role_a_name, role_b_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_input_api_data = get_input_api_data(background=f"{background_b} {post_prompt}",
                                               history=get_history(role_a_name, role_b_name, history),
                                               history_limit_turns=3)

    role_b_question = mask_instruct(role_b_input_api_data,
                                    temperature=selected_temp)

    print(f"{role_b_name}: ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    return '', history


def toggle(user_message, selected_temp, chatbot, background_b, role_a_name, role_b_name):
    user_message, history = role_b_chat(selected_temp, user_message, chatbot, background_b, role_a_name,
                                        role_b_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f():
    return None, None


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------


def update_select_model():
    return None, None


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

                with gr.Row():
                    user_name = gr.Textbox(lines=1, label="name of human", interactive=False, value='user')
                    bot_name = gr.Textbox(lines=1, label='name of bot', interactive=False, value='Angelie')
                background_role_b = gr.Textbox(lines=5, value=default_background, label="background of bot",
                                               interactive=False)
                role_a_question = gr.Textbox(placeholder="input your question and Press Enter to send.",
                                             label="question", interactive=True)
            with gr.Column():
                gr_chatbot = gr.Chatbot(label="chat bot")
                clear = gr.Button("clear history")

        clear.click(clear_f, None, [gr_chatbot, role_a_question])
        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_b, user_name,
                                       bot_name],
                               outputs=[role_a_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8906, debug=True)
