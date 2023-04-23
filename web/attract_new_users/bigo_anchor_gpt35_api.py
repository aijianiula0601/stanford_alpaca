import os
import time

import openai

# -------------------------------------
# 链接：
# https://platform.openai.com/docs/guides/chat/introduction
# -------------------------------------

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "a15cfae7bd4c47d68172e85649653725"

# role : system|user|assistant
gpt_config = {'engine': 'bigo-gpt35',
              'role': 'user',
              }


def chat_with_chatgpt(messages, selected_temp=0.95):
    response = openai.ChatCompletion.create(
        engine='bigo-gpt35',
        temperature=selected_temp,
        messages=messages
    )
    response_text = response.choices[0].message.content
    return response_text


def get_input_api_data(background, user_name, anchor_name, history=[]):
    data_list = [{'role': 'system', 'content': background}]
    for qa in history:
        if qa[0] is not None:
            data_list.append({'role': 'assistant', 'content': qa[0].lstrip(f"{anchor_name}: ")})
        if qa[1] is not None:
            data_list.append({"role": 'user', "content": qa[1].lstrip(f"{user_name}: ")})

    return data_list


background_pre_text = "Let's play a role game."

# background_post_text = "{role_name_a} can always attract others tightly at the beginning of the chat.  \
# The following is a chat between {role_name_b} and {role_name_a} using English Language. \
# Question and answer, forbid the output of multiple rounds. \
# after 4 rounds chat, {role_name_a} will send a Invitation with http link: Would you like to join my live-room for deeper communication?"

background_post_text = "You are {role_name_a}. I am {role_name_b}. Let's have a conversation. Ask me questions first. You go."


def get_background(background, role_name_a, role_name_b):
    bk_post = background_post_text.format_map({"role_name_a": role_name_a, "role_name_b": role_name_b})
    return f"{background_pre_text}\n{background}\n{bk_post}"


if __name__ == '__main__':
    # messages = [
    #     {"role": "system",
    #      "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
    #     {"role": "user", "content": "hi, Kervin"},
    #     {"role": "assistant", "content": "I am fine, how about you?"},
    #     {"role": "user", "content": "Where are you?"},
    #     {"role": "assistant", "content": "I am at home, what about you?"},
    #     {"role": "user", "content": "Let's go to the library. Will you come with me?"}
    # ]

    messages = [
        {"role": "system",
         "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice. Let's have a conversation. Ask me questions first. You go."},
        {"role": "assistant", "content": "Hi Alice! How are you doing today?"},
        {"role": "user", "content": "I am fine. where are you going?"},
    ]

    rs = chat_with_chatgpt(messages)
    print(rs)
