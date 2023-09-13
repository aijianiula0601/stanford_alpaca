import json
import openai
import re

import prompt_config as config


def get_gpt_result(engine_name: str, message_list: list, selected_temp: float = 0.7):
    response = openai.ChatCompletion.create(
        engine=engine_name,
        messages=message_list,
        temperature=selected_temp,
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


class ChatObject:
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
        if gpt_version == "gpt3.5":
            openai.api_type = "azure"
            openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
            openai.api_version = "2023-03-15-preview"
            openai.api_key = "0ea6b47ac9e3423cab22106d4db65d9d"
            self.engine_name = "bigo-gpt35"
            print(f"set gpt engine_name to:{self.engine_name}")
        elif gpt_version == 'gpt4':
            openai.api_type = "azure"
            openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
            openai.api_version = "2023-03-15-preview"
            openai.api_key = "bca8eef9f9c04c7bb1e573b4353e71ae"
            self.engine_name = "gpt4-16k"
            print(f"set gpt engine_name to:{self.engine_name}")
        else:
            raise EnvironmentError("must be set the gpt environment")

    def question_response(self, latest_history: str, current_user_question: str, selected_temp: float = 0.7):
        """获取用户问题答案"""

        format_map_dic = {
            'persona_background': self.persona['background'],
            'latest_history': latest_history,
            'current_user_question': current_user_question,

        }
        prompt = config.PROMPT_DIC['chat'].format_map(format_map_dic)
        message_list = [{"role": 'system', 'content': prompt}, {"role": 'user', 'content': current_user_question}]
        res = get_gpt_result(self.engine_name, message_list, selected_temp)

        print("-" * 100)
        print("prompt:")
        print(prompt)
        print("-" * 100)

        return res
