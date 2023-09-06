import json
import openai
import re

import config


def get_gpt_result(engine_name: str, role: str, content: str):
    message_list = [{"role": role, 'content': content}]
    response = openai.ChatCompletion.create(
        engine=engine_name,
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    return response['choices'][0]['message']['content']


def parse_intention_state(intention_status_analysis_text: str, key: str):
    pattern = r'"{0}":\s*"([^"]*)"'.format(key)
    match = re.search(pattern, intention_status_analysis_text)
    if match:
        value = match.group(1)
        return value
    else:
        return None


class ChainOfThoughtChat:
    def __init__(self, role_name="Angelie", gpt_version: str = '3.5'):
        self.full_message_history = []
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]
        self.engine_name = gpt_version

    def set_role(self, role_name):
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]

    def set_gpt_env(self, gpt_version: str = 3.5):
        """设置gpt接口类型，3.5还是4"""
        if gpt_version == "3.5":
            openai.api_type = "azure"
            openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
            openai.api_version = "2023-03-15-preview"
            openai.api_key = "0ea6b47ac9e3423cab22106d4db65d9d"
            self.engine_name = "bigo-gpt35"
        if gpt_version == '4':
            openai.api_type = "azure"
            openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
            openai.api_version = "2023-03-15-preview"
            openai.api_key = "bca8eef9f9c04c7bb1e573b4353e71ae"
            self.engine_name = "gpt4-16k"

    def question_response(self, last_summary: str, latest_history: str, current_user_question: str, user_state: str,
                          user_intention: str):
        """获取用户问题答案"""

        format_map_dic = {
            'persona_background': self.persona['background'],
            'last_summary': last_summary,
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            'user_state': user_state,
            'user_intention': user_intention,

        }
        prompt = config.PROMPT_DIC['chat'].format_map(format_map_dic)

        print("-" * 100)
        print('question_response')
        print("-" * 100)
        print(f'prompt:\n{prompt}')
        res = get_gpt_result(self.engine_name, role="user", content=prompt)
        print("=" * 20)
        print("res:")
        print("=" * 20)
        print(res)
        print("-" * 100)

        return res

    def intention_status_analysis(self, chat_history: str, user_question: str):
        """用户提问的意图的状态分析"""

        format_map_dic = {
            'chat_history': chat_history,
            'user_question': user_question,
        }
        prompt = config.PROMPT_DIC['intention_state'].format_map(format_map_dic)
        res_text = get_gpt_result(self.engine_name, role="user", content=prompt)
        intention = parse_intention_state(res_text, 'user_intention')
        state = parse_intention_state(res_text, 'user_state')

        print("-" * 100)
        print('intention_status_analysis')
        print("-" * 100)
        print(f'prompt:\n{prompt}')
        print("=" * 20)
        print(f"res:")
        print("=" * 20)
        print(res_text)

        return res_text, intention, state

    def history_summary(self, chat_history: str, last_summary: str = ""):
        """
        历史信息总结
        不是每一轮都总结历史，而是特定轮次后才总结。
        """

        format_map_dic = {
            "chat_history": chat_history,
            "last_summary": last_summary,
        }
        prompt = config.PROMPT_DIC['history_summary'].format_map(format_map_dic)

        return get_gpt_result(self.engine_name, role="user", content=prompt)
