import re
import logging
import openai


def get_gpt4_response(message_list: list):
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
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    return response['choices'][0]['message']['content']


def get_gpt35_response(message_list: list):
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
        temperature=0.6,
        messages=message_list
    )

    return response['choices'][0]['message']['content']


def parse_key_value(text: str, key: str):
    text = text.replace('\\"', '\'')
    partten = '"' + key + '":\s*"*([^"]*)"*'
    match = re.search(partten, text)
    if match:
        value = match.group(1).strip("\n }")
        return value
    else:
        return ""


def parse_result_of_analysis_chat(res_text: str):
    short_summary = parse_key_value(res_text, "short_summary")
    user_intention = parse_key_value(res_text, "user_intention")
    whatsapp = True if 'yes' in parse_key_value(res_text, "whatsapp").lower() else False
    picture = True if 'yes' in parse_key_value(res_text, "picture").lower() else False
    sex = True if 'yes' in parse_key_value(res_text, "sex").lower() else False
    negative = True if 'yes' in parse_key_value(res_text, "negative").lower() else False
    question = True if 'yes' in parse_key_value(res_text, "question").lower() else False

    if whatsapp:
        chat_state = 'whatsapp'
    elif picture:
        chat_state = 'picture'
    elif sex:
        chat_state = 'sex'
    elif negative and not question: # 用户回复消极且没有问问题的时候进入telling状态
        chat_state = 'telling'
    else:
        chat_state = 'normal'

    willingness_dict = {"whatsapp": 2, "picture": 2, "telling": 1, "sex": 2, "real": 1, "normal": 2}
    willingness_score = willingness_dict[chat_state]

    story_topic = parse_key_value(res_text, "story_topic")

    return short_summary, user_intention, chat_state, story_topic, willingness_score


def keywords_matching(keyword_list, current_user_question):
    print(current_user_question)
    if current_user_question == "":
        return False
    words_list_of_current_user_question = [x.strip('\'",.-()*&^%$#@!~+_-=').lower() for x in current_user_question.strip().split()]
    res = False
    for keyword in keyword_list:
        if keyword in words_list_of_current_user_question:
            res = True
    return res


def edit_distance_of_sentence(a, b):
    # 该函数只计算插入和替换错误，不计算删除错误。
    # 也就是说，如果用户的句子中包含了目标文本，多说的话不计算为错误。
    # b = 'Sure, here is my photo, which is about travel.'

    a = [x.strip(',.?!\'"') for x in a.lower().strip().split()]
    b = [x.strip(',.?!\'"') for x in b.lower().strip().split()]

    m, n = len(a) + 1, len(b) + 1
    d = [[0] * n for i in range(m)]

    d[0][0] = 0
    for i in range(1, m):
        d[i][0] = d[i - 1][0] + 1
    for j in range(1, n):
        d[0][j] = d[0][j - 1] + 1

    temp = 0
    for i in range(1, m):
        for j in range(1, n):
            if a[i - 1] == b[j - 1]:
                temp = 0
            else:
                temp = 1

            d[i][j] = min(d[i - 1][j], d[i][j - 1] + 1, d[i - 1][j - 1] + temp)
    # logging.debug("edit_distance_of_sentence: ", d[m-1][n-1])
    return d[m - 1][n - 1]


def is_exposed_AI_check(text):
    # 待完善更多case
    if 'AI language model' in text or 'OpenAI' in text:
        return True
    else:
        return False


def get_history_str(history: list):
    if len(history) <= 0:
        return ''
    history_list = []
    for qa in history:
        for q_a in qa:
            if q_a is not None and type(q_a) == str:
                history_list.append(q_a)
    return '\n'.join(history_list)


def get_latest_history(history: list, limit_turn_n: int):
    to_summary_history = []
    new_summary_flag = False
    if len(history) % limit_turn_n == 0 and len(history) // limit_turn_n > 1:
        if len(history) >= limit_turn_n * 2:
            new_summary_flag = True
            # 给过去做总结的历史
            to_summary_history = history[:-limit_turn_n][-limit_turn_n:]

    if new_summary_flag:
        latest_history = history[-limit_turn_n:]
    else:
        cur_turn_n = limit_turn_n + len(history) % limit_turn_n
        latest_history = history[-cur_turn_n:]

    return to_summary_history, latest_history
