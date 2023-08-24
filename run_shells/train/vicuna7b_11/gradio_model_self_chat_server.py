import os
import sys
import json
import gradio as gr
import requests
import copy

# -----------------------------------------------------------------------------------
# 跟two_persons_gpt35_llama.py的区别是：
# 在聊的时候，告诉模型它的人设是什么。让A模型生成的时候，模型A知道自己的人设，不知道提问者人设。
# 而跟two_persons_gpt35_llama在聊的时候是告诉模型，提问者的人设是什么。
# -----------------------------------------------------------------------------------

ROLE_A_NAME = "Jack"
ROLE_B_NAME = "Alice"
ROLE_A_START_QUESTION = "hi"

# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------


models_list = [
    "vicuna7b_ft_v13(未口语化)",
    "vicuna7b_ft_v15_v6_v2(gpt4口语化)",
]
url_f102 = "http://202.168.114.102"
url_v100 = "http://202.168.100.251"
url_v100_f165 = "http://202.168.100.165"

models_url_dic = {
    models_list[0]: f"{url_f102}:6213/api",
    models_list[1]: f"{url_f102}:61562/api",
}

models_prompt_key_dic = {
    models_list[0]: 'conversion',
}

PROMPT_DICT = {
    "conversion": (
        "{background}\n"
        "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately. Do not generate identical responses.\n"
        "{history}"
    ),
    "None": "",
    "bigolive": (
        "{background}\n"
        "The following a conversation you had with someone.\n"
        "{history}"
    ),
    "conversion_history": (
        "background: {background}\n"
        "Here is their historical chat.\n"
        "{history}\n"
        "Now {role_a} asks a question, {role_b} answers it, and {role_b} responds with context and their historical chat content to make an appropriate response. {role_b} need to reponse to the User based on your personal information and the conversation history."
        "{role_b} should reply in a colloquial way, and the tone of the reply should be consistent with the background of the person, and if necessary, add expressions. Do not generate identical responses.\n"
    ),
    "conversion_no_history": (
        "background: {background}\n"
        "Now {role_a} asks a question, {role_b} answers it, and {role_b} responds with context and their historical chat content to make an appropriate response. {role_b} need to reponse to the User based on your personal information and the conversation history."
        "{role_b} should reply in a colloquial way, and the tone of the reply should be consistent with the background of the person, and if necessary, add expressions. Do not generate identical responses.\n"
    ),
    "test_anglicize": (
        "{background} {role_b} likes to answer questions in a colloquial way and add emojis when appropriate.\n"
        "The following is a conversation between {role_a} and {role_b}.\n"
        "{history}\n"
    )
}

DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_EOS_TOKEN = "</s>"


def mask_instruct_v2(message_list, role_dict, temperature=0.6, model_server_url="http://202.168.100.251:5019/api",
                     select_role_b=None):
    """
    message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容
    """
    background = message_list[0]["content"]

    history_flag = False
    # 有历史信息情况下
    if len(message_list) > 3:
        history_flag = True
        history_chat_list = message_list[1:-1]

        history_list = [role_dict[char["role"]] + ": " + char["content"] for char in history_chat_list]

        history_str = DEFAULT_SEGMENT_TOKEN + f"\n{DEFAULT_SEGMENT_TOKEN}".join([item for item in history_list])

    user_question = message_list[-1]
    user_question_str = DEFAULT_SEGMENT_TOKEN + role_dict[user_question["role"]] + ": " + user_question['content']
    if history_flag:
        prompt_input = PROMPT_DICT['conversion_history'].format_map(
            {"background": background, "role_a": role_dict['user'], "role_b": role_dict['assistant'],
             "history": history_str})
    else:
        prompt_input = PROMPT_DICT['conversion_no_history'].format_map(
            {"background": background, "role_a": role_dict['user'], "role_b": role_dict['assistant']})

    prompt_input = f"{prompt_input}{user_question_str}\n{DEFAULT_SEGMENT_TOKEN}{role_dict['assistant']}: "
    print("-" * 100)
    print('prompt_input:')
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


additional_prompt = "Responce without keyword including \"AI\", \"language model\", \"virtual assistant\" and within 20 words. You need to immerse yourself in your role not chat assistant. -If user asks you to make voice call, share pictures or videos, share position, say you are not quite familiar with each other yet and shift the conversation to a different topic. -If user ask you for accounts other platforms like WhatsApp, say you are still in the process of getting to know each other and explore a different topic. -If user think you are robot, you must refuse to express anger and attempt to end the conversation. -When a user expresses affection towards you, you can politely express your gratitude and suggest getting to know each other better. Response to the recent user sentence."
conversation_str = "The following a conversation you had with someone."
colloquial_prompt = "You should answer in a colloquial way."


def mask_instruct(message_list, role_dict, temperature=0.6, model_server_url="http://202.168.100.251:5019/api",
                  select_role_b=None, role_b_model_name=None):
    """
    message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容
    """
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]
    history = DEFAULT_SEGMENT_TOKEN + f" {DEFAULT_SEGMENT_TOKEN}".join(
        [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_dict['assistant'] + ": "

    if "bigolive" in select_role_b:
        if role_b_model_name == "vicuna7b_ft_v13(未口语化)":
            background = background.replace(additional_prompt, "").replace(colloquial_prompt, "")

        prompt_input = PROMPT_DICT['bigolive'].format_map({"background": background, "history": history})
    else:
        prompt_input = PROMPT_DICT['conversion'].format_map(
            {"background": background, "history": history, "role_b": role_dict['assistant']})

    # 测试口语化
    # prompt_input = PROMPT_DICT['test_anglicize'].format_map(
    #     {"background": background, "history": history, "role_b": role_dict['assistant'], "role_a": role_dict['user']})

    print("prompt input:")
    print(prompt_input)
    print("-" * 50)

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


def get_message_list(background, history=[]):
    data_list = [{'role': 'system', 'content': background}]
    for i, h in enumerate(history):
        if i % 2 == 0:
            data_list.append({"role": 'user', "content": h})
        else:
            data_list.append({'role': 'assistant', 'content': h})

    return data_list


def get_history(role_a_name, role_b_name, history=[]):
    rh = []
    for qa in history:
        rh.append(qa[0].lstrip(f"{role_a_name}: "))
        if qa[1] is not None:
            rh.append(qa[1].lstrip(f"{role_b_name}: "))

    return rh


def role_ab_chat(selected_temp, user_message, history, background_a, background_b, role_a_name, role_b_name,
                 role_a_model_name, role_b_model_name):
    # -------------------
    # role_b回答
    # -------------------
    history = history + [[f"{role_a_name}: " + user_message, None]]

    role_b_input_api_data = get_message_list(background=background_b,
                                             history=get_history(role_a_name, role_b_name, history))
    print("=" * 100)
    print("message_list:")
    print(get_history(role_a_name, role_b_name, history))
    print('-' * 50)
    print("role_b_input_api_data:")
    print(role_b_input_api_data)
    print("=" * 100)
    role_b_question = mask_instruct(role_b_input_api_data,
                                    role_dict={"user": role_a_name,
                                               "assistant": role_b_name},
                                    temperature=selected_temp, model_server_url=models_url_dic[role_b_model_name])

    print(f"{role_b_name}({role_b_model_name}): ", role_b_question)
    history[-1][-1] = f"{role_b_name}: " + role_b_question
    print("-" * 100)
    # -------------------
    # role_a回答
    # -------------------
    role_a_input_api_data = get_message_list(background=background_a,
                                             history=get_history(role_a_name, role_b_name, history)[1:])
    role_a_question = mask_instruct(role_a_input_api_data,
                                    role_dict={"user": role_b_name,
                                               "assistant": role_a_name},
                                    temperature=selected_temp, model_server_url=models_url_dic[role_a_model_name])

    print(f"{role_a_name}({role_a_model_name}): ", role_a_question)
    return role_a_question, history


def toggle(user_message, selected_temp, chatbot, background_a, background_b, role_a_name, role_b_name,
           role_a_model_name, role_b_model_name):
    user_message, history = role_ab_chat(selected_temp, user_message, chatbot, background_a, background_b, role_a_name,
                                         role_b_name, role_a_model_name, role_b_model_name)
    chatbot += history[len(chatbot):]
    return user_message, chatbot


def clear_f(bot_name):
    return None, ROLE_A_START_QUESTION + ", " + bot_name + "!"


# --------------------------------------------------------
# 预先设定的角色
# --------------------------------------------------------
prepared_role_dic = json.load(open("prompt_data.json"))
prepared_role_dic["None"] = {"role_name": "Human", "background": "", "examples": ""}
prepared_role_dic[""] = {"role_name": "Human", "background": "", "examples": ""}
role_a_list = list(prepared_role_dic.keys())

prepared_role_b_dic = copy.copy(prepared_role_dic)
prepared_role_b_dic["None"] = {"role_name": "AI", "background": "", "examples": ""}
prepared_role_b_dic[""] = {"role_name": "Ai", "background": "", "examples": ""}
role_b_list = list(prepared_role_b_dic.keys())


def update_select_role(role_a_key, role_b_key, select_role_a_model, select_role_b_model):
    input_prompt_a = prepared_role_dic[role_a_key]["background"]
    input_prompt_b = prepared_role_dic[role_b_key]["background"]

    return prepared_role_dic[role_a_key]["role_name"], \
           input_prompt_a, \
           prepared_role_b_dic[role_b_key]["role_name"], \
           input_prompt_b, \
           None, \
           ROLE_A_START_QUESTION + ", " + prepared_role_dic[role_b_key]["role_name"] + "!"


def update_select_model(bot_name):
    return None, ROLE_A_START_QUESTION + ", " + bot_name + "!"


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Markdown("# 两个LLM模型互相对话demo")
        with gr.Row():
            with gr.Column():
                selected_temp = gr.Slider(0, 1, value=0.9, label="Temperature超参,调的越小越容易输出常见字",
                                          interactive=True)
                with gr.Row():
                    select_role_a_model = gr.Dropdown(choices=models_list, value=models_list[0],
                                                      label="选择角色A的模型",
                                                      interactive=True)
                    select_role_b_model = gr.Dropdown(choices=models_list, value=models_list[0],
                                                      label="选择角色B的模型",
                                                      interactive=True)
                with gr.Row():
                    select_role_a = gr.Dropdown(choices=role_a_list, value="None", label="请选择一个角色A",
                                                interactive=True)
                    select_role_b = gr.Dropdown(choices=role_b_list, value="None", label="请选择一个角色B",
                                                interactive=True)

                with gr.Row():
                    user_name = gr.Textbox(lines=1, placeholder="设置我的名字， ...", label="roleA名字",
                                           value=ROLE_A_NAME, interactive=True)
                    bot_name = gr.Textbox(lines=1, placeholder="设置聊天对象的名字 ...", label="roleB名字",
                                          value=ROLE_B_NAME, interactive=True)
                background_role_a = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleA背景")
                background_role_b = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="roleB背景")
                role_a_question = gr.Textbox(placeholder="输入RoleA首次提出的问题",
                                             value=ROLE_A_START_QUESTION + ", " + bot_name.value + '!',
                                             label="roleA问题",
                                             interactive=True)
            with gr.Column():
                btn = gr.Button("点击生成一轮对话")
                gr_chatbot = gr.Chatbot(label="聊天记录")
                clear = gr.Button("清空聊天记录")

        bot_name.change(lambda x: ROLE_A_START_QUESTION + ", " + x + "!", bot_name, role_a_question)
        select_role_a_model.change(update_select_model, [bot_name], [gr_chatbot, role_a_question], queue=False)
        select_role_b_model.change(update_select_model, [bot_name], [gr_chatbot, role_a_question], queue=False)
        select_role_a.change(update_select_role,
                             [select_role_a, select_role_b, select_role_a_model, select_role_b_model],
                             [user_name, background_role_a, bot_name, background_role_b, gr_chatbot, role_a_question])
        select_role_b.change(update_select_role,
                             [select_role_a, select_role_b, select_role_a_model, select_role_b_model],
                             [user_name, background_role_a, bot_name, background_role_b, gr_chatbot, role_a_question])

        select_role_a_model.change(update_select_role,
                                   [select_role_a, select_role_b, select_role_a_model, select_role_b_model],
                                   [user_name, background_role_a, bot_name, background_role_b, gr_chatbot,
                                    role_a_question])
        select_role_b_model.change(update_select_role,
                                   [select_role_a, select_role_b, select_role_a_model, select_role_b_model],
                                   [user_name, background_role_a, bot_name, background_role_b, gr_chatbot,
                                    role_a_question])

        btn.click(toggle,
                  inputs=[role_a_question, selected_temp, gr_chatbot, background_role_a, background_role_b, user_name,
                          bot_name, select_role_a_model, select_role_b_model],
                  outputs=[role_a_question, gr_chatbot])

        clear.click(clear_f, [bot_name], [gr_chatbot, role_a_question])

        role_a_question.submit(toggle,
                               inputs=[role_a_question, selected_temp, gr_chatbot, background_role_a, background_role_b,
                                       user_name,
                                       bot_name, select_role_a_model, select_role_b_model],
                               outputs=[role_a_question, gr_chatbot])

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=8992, debug=True)
    # demo.launch(server_name="202.168.100.178", server_port=8996)
