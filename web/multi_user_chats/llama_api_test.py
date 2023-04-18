import requests
import json
import os
import sys
import gradio as gr

# from utils import stringQ2B, post_filter
pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)

PROMPT_DICT = {
    "conversion": (
        # "The following is a chat message between {role_a} and {role_b}. Question and answer, forbid the output of multiple rounds. {background}\n\n"
        "{background}. The following is a chat message between {role_a} and {role_b} using English Language. Question and answer, forbid the output of multiple rounds.\n\n"
        "Current conversation:\n\n"
        "{history}"
    )
}


def llama_respond(message_list, role_dict, temperature=0.6):
    '''message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案'''
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]

    cur_history = {"background": background,
                   "role_a": role_dict['user'],
                   "role_b": role_dict['assistant'],
                   "history": "\n".join([item for item in history_list]) + "\n" + role_dict['assistant'] + ": "}
    prompt_input = PROMPT_DICT["conversion"].format_map(cur_history)

    request_data = json.dumps({
        "history": prompt_input,
        "temperature": temperature,
        "max_gen_len": 256,
        "background": "",
        "role_a": role_dict['user'],
        "role_b": role_dict['assistant'],
    })
    response = requests.post("http://202.168.100.182:805/api/llama", data=request_data)
    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    text_respond = text_respond.strip().split(role_dict['user'])[0]
    return text_respond.strip()


if __name__ == '__main__':
    message_list_orign = [
        {"role": "system",
         "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
        {"role": "user", "content": "hi, Kervin"},
        {"role": "assistant", "content": "I am fine, how about you?"},
        {"role": "user", "content": "Where are you?"},
        {"role": "assistant", "content": "I am at home, what about you?"},
        {"role": "user", "content": "Let's go to the library. Will you come with me?"}
    ]

    role_dict = {
        "user": "Alice",
        "assistant": "Kervin"
    }

    rs = llama_respond(message_list_orign, role_dict)
    print(rs)
