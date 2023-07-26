import os
import sys
import json
import requests
import copy
import random

ROLE_A_NAME = "Jack"
ROLE_B_NAME = "Alice"
ROLE_A_START_QUESTION = "hi"

# --------------------------------------------------------
# 模型选择
# --------------------------------------------------------


models_list = [
    "vicuna7b_ft_bigolive",
    "vicuna7b_ft_multitype_bigolive",
    "llama2_v0",
]
url_f102 = "http://202.168.114.102"
url_v100 = "http://202.168.114.102"

# 每个模型服务的地址
models_url_dic = {
    models_list[0]: [f"{url_f102}:60244/api"],
    models_list[1]: [f"{url_f102}:60213/api"],
    models_list[2]: [f"{url_f102}:7000/api"],
}

models_prompt_key_dic = {
    models_list[0]: 'conversion',
}

PROMPT_DICT = {
    "conversion": (
        "{background}\n"
        "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately. Do not generate identical responses.\n"
    ),
    "None": "",
    "bigolive": (
        "{background} Keep your responses short. Don't ask multiple questions at once. \n"
    ),
}

DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_EOS_TOKEN = "</s>"


def mask_instruct(message_list, role_dict, temperature=0.6, model_server_url="http://202.168.114.102:60244/api"):
    """
    message-list:
        [
            {"role": "system","content": "~"},
            {"role": "user", "content": "~"},
            {"role": "assistant", "content": "~"},
            {"role": "user", "content": "~"}
        ]

    role_dict:
        {"user": "~", "assistant": "~"}

    """
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]
    history = DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
        [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_dict['assistant'] + ":"

    # prompt_bk = PROMPT_DICT['bigolive'].format_map({"background": background, "role_b": role_dict['assistant']})
    prompt_input = f"{background}\n{history}"

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


def post_data_trans(post_data: dict):
    """
    转换为如下格式：
    [
        {"role": "system","content": "~"},
        {"role": "user", "content": "~"},
        {"role": "assistant", "content": "~"},
        {"role": "user", "content": "~"}
    ]
    """
    role_dic = {"user": post_data["role_a"], "assistant": post_data['role_b']}
    message_list = [{"role": "system", "content": post_data['background']}]
    for qa in post_data['qas']:
        message_list.append({"role": "user", "content": qa['question']})
        if 'answer' in qa:
            message_list.append({"role": "assistant", "content": qa['answer']})

    return message_list, role_dic


def get_model_server_url(model_name):
    return random.sample(models_url_dic[model_name], k=1)[0]


if __name__ == '__main__':
    post_data = {"role_id": "3", "qas": [{"turn_i": 0, "question": "hi"}],
                 "background": "Britney sounds absolutely scandalous, Britney is a married female teacher with fair skin, beautiful appearance and gentle personality. Britney is a natural stunner and is the object of obscenity. Britney is seduced by her boss and other men, and Britney is involved in a The promiscuous life, the orgasms made him lose himself again and again, Britney enjoyed this feeling more and more, and enjoyed having sex with different men every day. Britney can't help but start to writhe when Britney sees a man's dick now, ready get fucked. Britney is talkative, always speak a lot in conversion. Britney needs to actively answer questions.",
                 "role_a": "Jack", "role_b": "Britney"}

    message_list, role_dic = post_data_trans(post_data)
    print(message_list)
    print(role_dic)
    # 调用测试
    res = mask_instruct(message_list, role_dic,model_server_url="http://202.168.100.165:5018/api")
    print(res)
