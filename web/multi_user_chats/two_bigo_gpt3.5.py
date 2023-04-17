import os
import time

import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "a15cfae7bd4c47d68172e85649653725"

# role : system|user|assistant
gpt_config = {'engine': 'bigo-gpt35',
              'role': 'user',
              }


def chat_with_chatgpt(prompt, role_a_name, role_b_name):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[f" {role_a_name}:", f" {role_b_name}:"]
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


background_post_text = "The following is a conversation with {role_name_a} and {role_name_a} "


def get_background(background, role_name_a, role_name_b):
    return background.format_map({"role_name_a": role_name_a, "role_name_b": role_name_b})


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

    role_a_question = start_question
    history = [start_question]

    # role_b_input_api_data = get_input_api_data(get_background(backgroundB, role_B_name, role_A_name),
    #                                            history=[])
    # role_b_question = chat_with_chatgpt(role_b_input_api_data, user=role_B_name)
    # print("role_b_question:", role_b_question)

    while True:
        role_b_input_api_data = get_input_api_data(get_background(backgroundB, role_B_name, role_A_name),
                                                   history=history)

        print("---role_b_input_api_data:", role_b_input_api_data)
        role_b_question = chat_with_chatgpt(role_b_input_api_data, user=role_A_name)
        print(f"{role_B_name}:", role_b_question)
        history.append(role_b_question)
        time.sleep(3)

        print("=" * 20)

        role_a_input_api_data = get_input_api_data(get_background(backgroundA, role_A_name, role_B_name),
                                                   history=history)
        print("---role_a_input_api_data:", role_a_input_api_data)
        role_a_question = chat_with_chatgpt(role_a_question, user=role_B_name)
        print(f"{role_A_name}:", role_a_question)
        history.append(role_a_question)
        print("-" * 100)
        print()
        print()
