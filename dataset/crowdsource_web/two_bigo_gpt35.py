import os
import time

import openai

# -------------------------------------
# 链接：
# https://platform.openai.com/docs/guides/chat/introduction
# -------------------------------------

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# ----------------
# 非线上的key
# ----------------
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"

# role : system|user|assistant
gpt_config = {'engine': 'gpt-35-turbo',
              'role': 'user',
              }


def chat_with_chatgpt(messages, selected_temp=0.95):
    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
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
        role_b_input_api_data = get_input_api_data(background=backgroundB,
                                                   history=history)

        # print("---role_b_input_api_data:", role_b_input_api_data)
        role_b_question = chat_with_chatgpt(role_b_input_api_data)
        print(f"{role_B_name}:", role_b_question)
        history.append(role_b_question)
        time.sleep(3)
        print()
        print("-" * 100)

        role_a_input_api_data = get_input_api_data(backgroundA,
                                                   history=history[1:])
        # print("---role_a_input_api_data:", role_a_input_api_data)
        role_a_question = chat_with_chatgpt(role_a_input_api_data)
        print(f"{role_A_name}:", role_a_question)
        history.append(role_a_question)
