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
        engine='bigo-gpt35',
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[f"{role_a_name}:", f"{role_b_name}:"]
    )
    return response.choices[0].text


background_post_text = "The following is a conversation with {role_name_a} and {role_name_a}.\n\n"


def get_background(background, role_name_a, role_name_b):
    return background + "\n\n" + background_post_text.format_map(
        {"role_name_a": role_name_a, "role_name_b": role_name_b})


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
    prompt = get_background(backgroundA, role_A_name,
                            role_B_name) + f"{role_A_name}:{role_a_question}\n{role_B_name}:"
    while True:
        role_b_question = chat_with_chatgpt(prompt, role_A_name, role_B_name)
        print(f"{role_B_name}:", role_b_question)
        prompt += f"{role_b_question}\n{role_A_name}:"
        role_a_question = chat_with_chatgpt(prompt, role_A_name, role_B_name)
        print(f"{role_A_name}:", role_a_question)
        prompt += f"{role_a_question}\n{role_B_name}:"
