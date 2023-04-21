import os
import time

import openai

# -------------------------------------
# 链接：
# https://platform.openai.com/docs/guides/chat/introduction
# -------------------------------------

# 俊仕
# openai.api_key='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'
# 程琦
# openai.api_key = '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'
# 陈江
# openai.api_key = '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'
# 庞永强
openai.api_key = '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'

messages = [
    {"role": "system",
     "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
    {"role": "user", "content": "hi, Kervin"},
    {"role": "assistant", "content": "I am fine, how about you?"},
    {"role": "user", "content": "Where are you?"},
    {"role": "assistant", "content": "I am at home, what about you?"},
    {"role": "user", "content": "Let's go to the library. Will you come with me?"}
]


def chat_with_chatgpt(messages, selected_temp=0.95):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=selected_temp,
        messages=messages
    )
    response_text = response.choices[0].message.content
    return response_text


def get_input_api_data(background, history=[]):
    data_list = [{'role': 'system', 'content': background}]
    for i, h in enumerate(history):
        if i % 2 == 0:
            data_list.append({"role": 'user', "content": h})
        else:
            data_list.append({'role': 'assistant', 'content': h})

    return data_list


background_pre_text = "Let's play a role game."
background_post_text = "You are {role_name_a}. I am {role_name_b} "


def get_background(background, role_name_a, role_name_b):
    bk_post = background_post_text.format_map({"role_name_a": role_name_a, "role_name_b": role_name_b})
    return f"{background_pre_text}\n{background}\n{bk_post}"


if __name__ == '__main__':
    backgroundA = input("输入角色A的人设:")
    backgroundB = input("输入角色B的人设:")
    role_A_name = input("输入角色A的名字:")
    role_B_name = input("输入角色B的名字:")
    print("-" * 50 + "您输入的信息" + "-" * 50)
    print("角色A的人设信息为：", backgroundA)
    print("角色B的人设信息为：", backgroundB)
    print("角色A名字：", role_A_name)
    print("角色B名字：", role_B_name)
    print("-" * 106)
    start_question = input("输入初始问题(角色A提问)：")
    print(f"{role_A_name}:", start_question)

    history = [start_question]

    while True:
        role_b_input_api_data = get_input_api_data(background=get_background(backgroundB, role_B_name, role_A_name),
                                                   history=history)

        # print("---role_b_input_api_data:", role_b_input_api_data)
        role_b_question = chat_with_chatgpt(role_b_input_api_data)
        print(f"{role_B_name}:", role_b_question)
        history.append(role_b_question)
        time.sleep(3)
        print()
        print("-" * 100)

        role_a_input_api_data = get_input_api_data(get_background(backgroundA, role_A_name, role_B_name),
                                                   history=history[1:])
        # print("---role_a_input_api_data:", role_a_input_api_data)
        role_a_question = chat_with_chatgpt(role_a_input_api_data)
        print(f"{role_A_name}:", role_a_question)
        history.append(role_a_question)
