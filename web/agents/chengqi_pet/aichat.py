import json
import openai
import re
import time
import config


def get_gpt_result(engine_name: str, message_list: list):
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
    pattern = r'"{0}"\s*:\s*("[^"]*"|[^",]*)'.format(key)
    # pattern = r'"{0}"：\s*"([^"]*)"'.format(key)
    
    match = re.search(pattern, intention_status_analysis_text)
    if match:
        value = match.group(1)
        return value
    else:
        pattern = r'"{0}"\s*：\s*("[^"]*"|[^",]*)'.format(key)
        match = re.search(pattern, intention_status_analysis_text)
        if match:
            value = match.group(1)
            return value
        else:
            return None


class PetChat:
    def __init__(self, role_name="Rabit(pet)", gpt_version: str = '3.5'):
        self.full_message_history = []
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]
        self.engine_name = gpt_version

    def update_state(self):
        # self.state = StateMachine()
        pass


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

    def question_response(self, chat_type, latest_history, current_user_question, \
        now_time, now_feed, now_emotion, now_work, touch_type="", food_type=""):
        """获取用户问题答案"""
        format_map_dic = {
            'now_time': now_time,
            'now_feed': now_feed,
            'now_emotion': now_emotion,
            'persona_background': self.persona['background'],
            'food_like' : self.persona['food_like'],
            'touch_like' : self.persona['touch_like'],
            'now_work': now_work,
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            'touch_type' : touch_type,
            'food_type' : food_type,

        }
        # assert chat_type in ["call_master", "touch", "feed", "greet_master", "chat_master"]
        prompt = config.PROMPT_DIC[chat_type].format_map(format_map_dic)

        if current_user_question is None or current_user_question == '':
            message_list = [{"role": 'user', 'content': prompt}]
        else:
            message_list = [{"role": 'system', 'content': prompt}, {"role": 'user', 'content': current_user_question}]

        res = get_gpt_result(self.engine_name, message_list)

        print("-" * 100)
        print('question_response')
        print("-" * 100)
        print(f'prompt:\n{prompt}')
        print("=" * 20)
        print(f"res:{res}")
        print("=" * 20)
        print("-" * 100)

        if ":" in res:
            res = res.split(":")[-1]

        if chat_type not in ["greet_master", "chat_master"]:
            res = "[" + now_time + "] " + res + "[" + chat_type + "]"

        return res

    def status_analysis(self, now_time, now_feed, now_emotion, today_work, time_radio):
        """小鸡当前状态分析"""

        # 计算增加一小时后的时间戳
        parsed_time = time.strptime(now_time, "%H:%M:%S")
        # 增加1小时
        time_radio_h = float(time_radio.replace("h", ""))
        new_time = time.mktime(parsed_time) + 3600 * time_radio_h
        # 将新时间转换为struct_time对象
        new_time_struct = time.localtime(new_time)
        # 将struct_time对象转换为字符串形式
        now_time = time.strftime("%H:%M:%S", new_time_struct)

        format_map_dic = {
            'now_time': now_time,
            'now_feed': now_feed,
            'now_emotion': now_emotion,
            'persona_background': self.persona['background'],
            'today_work': today_work,
            'last_time_h': time_radio.replace("h", "")
        }
        prompt = config.PROMPT_DIC['petplan'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(self.engine_name, message_list)

        #饱食度、心情、现在工作、今日总结
        now_feed = parse_intention_state(res_text, '饱食度')
        now_emotion = parse_intention_state(res_text, '心情')
        now_work = parse_intention_state(res_text, '当前活动')
        today_summary = parse_intention_state(res_text, '今日总结')

        print("-" * 100)
        print('intention_status_analysis')
        print("-" * 100)
        print(f'prompt:\n{prompt}')
        print("=" * 20)
        print(f"res:{res_text}")
        print("=" * 20)

        return res_text, now_time, now_feed, now_emotion, now_work, today_summary