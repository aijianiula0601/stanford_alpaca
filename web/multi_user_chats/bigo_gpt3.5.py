import os
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "a15cfae7bd4c47d68172e85649653725"

# role : system|user|assistant
gpt_config = {'engine': 'bigo-gpt35',
              'role': 'user',
              }


def chat_with_chatgpt(content_list, user, role='user'):
    req_msg = list()
    for c in content_list:
        if isinstance(c, dict):
            req_msg.append(c)
        elif isinstance(c, str):
            req_msg.append({'role': role, 'content': c})
        else:
            return "not supported input format"
    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        messages=req_msg,
        user=user,
        temperature=1,
        max_tokens=5000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    print(response)
    print(response.choices[0].message.content)
    response_text = response.choices[0].message.content
    return response_text


if __name__ == '__main__':
    # 单轮聊天
    # chat_with_chatgpt(['who are you?'], user="hjh")
    # 有聊天记录的聊天
    chat_with_chatgpt([
        {'role': 'system', 'content': '你是一个总裁助理'},
        {'role': 'user', 'content': '查询今天飞浆航班，帮我订张机票'},
        {'role': 'assistant', 'content': '今天暴雨，所有航班取消了'},
        {'role': 'user', 'content': '那我今天行程是什么？'},

    ], user='hjh')
