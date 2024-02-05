import re
import openai


def _get_gpt4_response(message_list: list):
    """
    采用gpt4获取结果

    message_list:  [
        {"role": "system","content": "~"},
        {"role": "user", "content": "~"}

    ]
    """
    openai.api_type = "azure"
    openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        messages=message_list,
        temperature=0.9,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    return response['choices'][0]['message']['content']


def _get_gpt35_response(message_list: list):
    """
    采用gpt35获取结果
    message_list:  [
        {"role": "system","content": "~"},
        {"role": "user", "content": "~"}

    ]
    """
    openai.api_type = "azure"
    openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    # key1: 19ea901e8e10475da1bb0537abf8e5a4
    # key2: 548e5c0c2aff453e932948927a27bde6
    openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"

    response = openai.ChatCompletion.create(
        engine='gpt-35-turbo',
        temperature=0.9,
        messages=message_list
    )

    return response['choices'][0]['message']['content']


def get_gpt_response(message_list: list, gpt_version="gpt3.5"):
    """
    获取gpt答案
    message_list:  [
        {"role": "system","content": "~"},
        {"role": "user", "content": "~"}

    ]
    gpt_version: gpt3.5 or gpt4
    """
    if gpt_version == 'gpt3.5':
        res_text = _get_gpt35_response(message_list)
    elif gpt_version == "gpt4":
        res_text = _get_gpt4_response(message_list)

    else:
        raise KeyError(f"gpt_version:{gpt_version} error!")

    return res_text


def get_prompt_from_md(md_file: str, map_dic: dict):
    return ''.join(open(md_file, 'r', encoding='utf-8').readlines()).format_map(map_dic)


def keywords_matching(keyword_list, current_user_question):
    """
    关键词匹配

    keyword_list: 关键词列表
    current_user_question: 当前用户的问题
    """
    words_list_of_current_user_question = [x.strip('\'",.-()*&^%$#@!~+_-=').lower() for x in current_user_question.strip().split()]
    res = False
    for keyword in keyword_list:
        if keyword in words_list_of_current_user_question:
            res = True
    return res


def parse_key_value(text: str, key: str):
    text = text.replace('\\"', '\'')
    partten = '"' + key + '":\s*"*([^"]*)"*'
    match = re.search(partten, text)
    if match:
        value = match.group(1).strip("\n }")
        return value
    else:
        return ""


def response_post_process(response_text: str):
    """
    gpt回复的问题后处理
    """

    return response_text.lstrip(".").strip().strip("rosa").strip(":").strip()


if __name__ == '__main__':
    # -------------------------------------
    # check whatapp.md
    # -------------------------------------
    md_file = "prompts/states/whatapp.md"
    map_dic = {
        "current_user_question": "Are you single?"
    }
    prompt = get_prompt_from_md(md_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]
    re_text = get_gpt35_response(message_list)
    print("-" * 100)
    print(prompt)
    print("-" * 100)
    print("re_text:", re_text)
