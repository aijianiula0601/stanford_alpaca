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


def llama_respond(message_list, role_dict, role_dict_real, temperature=0.6):
    '''message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容'''
    background = message_list[0]["content"]
    # history_list = [char["role"]+ ": " + char["content"] for char in message_list[1:]]
    history_list = [role_dict_real[char["role"]] + ": " + char["content"] for char in message_list[1:]]

    cur_history = {"background": background,
                   "role_a": role_dict['user'],
                   "role_b": role_dict['assistant'],
                   "history": "\n".join([item for item in history_list]) + "\n" + role_dict['assistant'] + ": "}
    prompt_input = PROMPT_DICT["conversion"].format_map(cur_history)

    request_data = json.dumps({
        "history": prompt_input,
        "temperature": 0.6,
        "max_gen_len": 256,
        "background": "",
        "role_a": role_dict['user'],
        "role_b": role_dict['assistant'],
    })

    response = requests.post("http://202.168.100.182:805/api/llama", data=request_data)
    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    # print("REAL Respond", text_respond)
    text_respond = text_respond.strip().split(role_dict['user'] + ": ")[0]
    return text_respond.strip()


if __name__ == '__main__':
    #------------
    # role_a
    #------------
    message_list_org = [{'role': 'system',
                         'content': "Let's play a role game.\nAlice and Kervin are classmate.\nYou are Kervin. I am Alice "},
                        {'role': 'user', 'content': 'hi, Kervin!'}]

    role_dict_real = {'user': 'Alice', 'assistant': 'Kervin'}
    role_dict = {'user': 'Alice', 'assistant': 'Kervin'}

    # print(llama_respond(message_list_org, role_dict, role_dict_real))

    #------------
    # role_b
    #------------
    message_list_org = [{'role': 'system',
                         'content': "Let's play a role game.\nAlice and Kervin are classmate.\nYou are Alice. I am Kervin "},
                        {'role': 'user', 'content': 'Hi there, Alice! How are you?'}]

    role_dict = {'user': 'Kervin', 'assistant': 'Alice'}
    # print(llama_respond(message_list_org, role_dict, role_dict_real))

    #------------
    # role_a
    #------------
    message_list_org = [{'role': 'system',
                         'content': "Let's play a role game.\nAlice and Kervin are classmate.\nYou are Kervin. I am Alice "},
                        {'role': 'user', 'content': 'hi, Kervin!'},
                        {'role': 'assistant', 'content': 'Hi there, Alice! How are you?'},
                        {'role': 'user', 'content': '🤩 Hi Kervin! It’s so nice to see you!'}
                        ]

    # ------------
    # role_b
    # ------------
    role_dict = {'user': 'Alice', 'assistant': 'Kervin'}
    print(llama_respond(message_list_org, role_dict, role_dict_real))

    message_list_org = [{'role': 'system',
                         'content': "Let's play a role game.\nAlice and Kervin are classmate.\nYou are Alice. I am Kervin."},
                        {'role': 'user', 'content': 'Hi there, Alice! How are you?'},
                        {'role': 'assistant', 'content': '🤩 Hi Kervin! It’s so nice to see you!'}
                        ]

    role_dict = {'user': 'Kervin', 'assistant': 'Alice'}
    print(llama_respond(message_list_org, role_dict, role_dict_real))

