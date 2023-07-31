import os
import sys
import json
import gradio as gr
import requests
import copy
import numpy as np

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print("pdj:", pdj)
sys.path.append(pdj)

# -----------------------------------------------------------------------------------
# 跟two_persons_gpt35_llama.py的区别是：
# 在聊的时候，告诉模型它的人设是什么。让A模型生成的时候，模型A知道自己的人设，不知道提问者人设。
# 而跟two_persons_gpt35_llama在聊的时候是告诉模型，提问者的人设是什么。
# -----------------------------------------------------------------------------------

HUMAN_NAME = "Jack"
BOT_NAME = "Ai"
BOT_START_QUESTION = "hi"

# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------

models_list = [
    "vicuna7b_ft2epoch_v2",
]
url_f102 = "http://202.168.114.102"
url_v100 = "http://202.168.100.251"
url_v100_f165 = "http://202.168.100.165"

models_url_dic = {
    models_list[0]: f"{url_v100_f165}:60292/api",
}

PROMPT_DICT = {
    "conversation": ("{background}\n"
                     "The following is a conversation between {human_name} and {bot_name}.\n\n"),
    "None": ""
}

DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_EOS_TOKEN = "</s>"


def get_input_api_data(background, history=[]):
    data_list = [{'role': 'system', 'content': background}]
    for i, h in enumerate(history):
        if i % 2 == 0:
            data_list.append({"role": 'user', "content": h})
        else:
            data_list.append({'role': 'assistant', 'content': h})

    return data_list


def mask_instruct(message_list, role_dict, temperature=0.6, model_server_url="http://202.168.100.251:5019/api"):
    """
    message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容
    """
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]
    history = DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
        [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_dict['assistant'] + ":"

    background_str = PROMPT_DICT['conversation'].format_map(
        {'background': background, 'human_name': role_dict['assistant'], 'bot_name': role_dict['user']})
    prompt_input = f"{background_str}{history}"

    print("-" * 50 + 'prompt_input' + "-" * 40)
    print(prompt_input)
    print("-" * 100)

    request_data = json.dumps({
        "prompt_input": prompt_input,
        "temperature": temperature,
        "role_b": role_dict['assistant'],
        "max_gen_len": 256,
        "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(), role_dict['user'] + ":", DEFAULT_EOS_TOKEN]
    })
    response = requests.post(model_server_url, data=request_data)

    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    return text_respond.replace("#", "").strip()


def get_history(user_name, assistant_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].strip().lstrip(f"{user_name}:").strip())
        if qa[1] is not None:
            rh.append(qa[1].strip().lstrip(f"{assistant_name}:").strip())

    return rh


def role_ab_chat(selected_temp, bot_message, history, background_human, background_bot, human_name, bot_name,
                 bot_model):
    # -------------------
    # human的回答
    # -------------------
    history = history + [[f"{bot_name}: " + bot_message, None]]

    input_human_api_data = get_input_api_data(background=background_human,
                                              history=get_history(bot_name, human_name, history))
    print("-" * 100 + "input_human_api_data:")
    print(input_human_api_data)
    human_question = mask_instruct(input_human_api_data,
                                   role_dict={"user": bot_name,
                                              "assistant": human_name},
                                   temperature=selected_temp, model_server_url=models_url_dic[bot_model])
    print(f"{human_name}: " + human_question)
    print()
    history[-1][-1] = f"{human_name}: " + human_question
    # -------------------
    # bot的回答
    # -------------------
    bot_history = []
    item = []
    for i, e in enumerate(list(np.array(history).flatten())[1:]):
        item.append(e)
        if i % 2 == 1:
            bot_history.append(copy.copy(item))
            item.clear()
    if len(item) == 1:
        item.append(None)
        bot_history.append(copy.copy(item))

    input_bot_api_data = get_input_api_data(background=background_bot,
                                            history=get_history(human_name, bot_name, bot_history))
    print(input_bot_api_data)
    print("-" * 100)
    bot_question = mask_instruct(input_bot_api_data,
                                 role_dict={"user": human_name,
                                            "assistant": bot_name},
                                 temperature=selected_temp, model_server_url=models_url_dic[bot_model])
    print(f"{bot_name}: " + bot_question)
    print("*" * 200)
    return bot_question, history


def toggle(bot_message, selected_temp, chatbot, background_human, background_bot, human_name, bot_name,
           select_bot_model):
    bot_message, history = role_ab_chat(selected_temp, bot_message, chatbot, background_human, background_bot,
                                        human_name,
                                        bot_name, select_bot_model)
    chatbot += history[len(chatbot):]
    return bot_message, chatbot


def clear_f(human_name):
    return None, BOT_START_QUESTION + ", " + human_name + "!"


# # --------------------------------------------------------
# # 预先设定的角色
# # --------------------------------------------------------
# prepared_role_dic = json.load(open(f"{pdj}/run_shells/infer/prepared_background.json"))
# prepared_role_dic["None"] = {"role_name": "Human", "background": "", "examples": ""}
# prepared_role_dic[""] = {"role_name": "Human", "background": "", "examples": ""}
# human_list = list(prepared_role_dic.keys())
#
# prepared_role_b_dic = copy.copy(prepared_role_dic)
# prepared_role_b_dic["None"] = {"role_name": "AI", "background": "", "examples": ""}
# prepared_role_b_dic[""] = {"role_name": "Ai", "background": "", "examples": ""}
# bot_list = list(prepared_role_b_dic.keys())


def update_select_model(bot_name):
    return None, BOT_START_QUESTION + ", " + bot_name + "!"


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# 微调mechat数据两模型互聊demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                          interactive=True)
                with gr.Row():
                    select_bot_model = gr.Dropdown(choices=models_list, value=models_list[0],
                                                   label="选择角色B的模型",
                                                   interactive=True)

                with gr.Row():
                    human_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="human名字",
                                            value=HUMAN_NAME, interactive=True)
                    bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="bot名字",
                                          value=BOT_NAME, interactive=True)

                background_bot = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="bot背景")
                bot_question = gr.Textbox(placeholder="输入RoleA首次提出的问题",
                                          value=BOT_START_QUESTION + ", " + human_name.value + '!',
                                          label="bot问题",
                                          interactive=True)
            with gr.Column():
                btn = gr.Button("点击生成一轮对话")
                gr_chatbot = gr.Chatbot(label="聊天记录")
                clear = gr.Button("清空聊天记录")

        bot_name.change(lambda x: BOT_START_QUESTION + ", " + x + "!", human_name, bot_question)
        select_bot_model.change(update_select_model, [bot_name], [gr_chatbot, bot_question], queue=False)

        btn.click(toggle,
                  inputs=[bot_question, selected_temp, gr_chatbot, background_bot, background_bot, human_name,
                          bot_name, select_bot_model],
                  outputs=[bot_question, gr_chatbot])

        clear.click(clear_f, [human_name], [gr_chatbot, bot_question])

        bot_question.submit(toggle,
                            inputs=[bot_question, selected_temp, gr_chatbot, background_bot, background_bot,
                                    human_name,
                                    bot_name, select_bot_model],
                            outputs=[bot_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8992, debug=True)
