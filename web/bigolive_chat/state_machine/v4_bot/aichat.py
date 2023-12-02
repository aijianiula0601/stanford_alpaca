import json
import openai
import re
import importlib
import config
import random
import logging


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


def parse_user_intention(text: str):
    match1 = re.search(r'"intention":\s*"*([^"]*)"*', text)
    match2 = re.search(r'"user_intention":\s*"*([^"]*)"*', text)
    if match1:
        value = match1.group(1)
        return value
    elif match2:
        value = match2.group(1)
        return value
    else:
        return None


def parse_chat_topic(text: str):
    match1 = re.search(r'"topic":\s*"*([^"]*)"*', text)
    match2 = re.search(r'"chat_topic":\s*"*([^"]*)"*', text)
    if match1:
        value = match1.group(1)
        return value
    elif match2:
        value = match2.group(1)
        return value
    else:
        return None


def parse_chat_state(text: str):
    match1 = re.search(r'"chat_state":\s*"*([^"]*)"*', text)
    match2 = re.search(r'"chat state":\s*"*([^"]*)"*', text)
    value = ""
    if match1:
        value = match1.group(1).strip("\n }")
    elif match2:
        value = match2.group(1).strip("\n }")

    match3 = re.search(r'[0-9]', value)
    if match3:
        index = match3.group(0)
    else:
        index = "1"
    state_key_dict = {"1": "normal", "2": "love", "3": "sex", "4": "telling", "5": "picture"}
    state = state_key_dict[index]

    return state


def keywords_matching(keyword_list, current_user_question):
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

    m,n = len(a)+1,len(b)+1
    d = [[0]*n for i in range(m)]

    d[0][0]=0
    for i in range(1,m):
        d[i][0] = d[i-1][0] + 1
    for j in range(1,n):
        d[0][j] = d[0][j-1]+1

    temp = 0
    for i in range(1,m):
        for j in range(1,n):
            if a[i-1]==b[j-1]:
                temp = 0
            else:
                temp = 1
            
            d[i][j]=min(d[i-1][j],d[i][j-1]+1,d[i-1][j-1]+temp)
    logging.debug("edit_distance_of_sentence: ", d[m-1][n-1])
    return d[m-1][n-1]


def parse_memory_dict(text, memory_dict):
    for key in memory_dict.keys():
        if memory_dict[key] != "unknown":
            continue
        pattern = '"' + key + '":\s*"*([^"]*)"*'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            memory_dict[key] = value
        else:
            memory_dict[key] = "unknown"
    return memory_dict
    

def is_exposed_AI_check(text):
    # 待完善更多case
    if 'AI language model' in text:
        return True
    else:
        return False

class StateMachine:
    def __init__(self) -> None:
        self.pre_state = 'greeting'
        self.current_state = "greeting"
        self.round_num = 0
        self.end_greeting_flag = False
        self.state_count_whatsapp = 0
        self.day = 1


    def __str__(self) -> str:
        res = ("round: {}\n"
        "current_state: {}\n"
        "day: {}\n"
        ).format(self.round_num, self.current_state, self.day)
        return res


    def update_day(self, pre_day_summary: str):
        self.current_state = "greeting"
        self.round_num = 0
        self.end_greeting_flag = False
        self.state_count_whatsapp = 0
        self.day += 1
        self.pre_day_summary = pre_day_summary


    def get_prompt(self, persona: dict, recent_status: str, last_summary: str, latest_history: str, current_user_question: str,
                    user_intention: str, pic_topics: str, current_time: str):
        if self.current_state == 'greeting':
            format_map_dic = {
            'name': persona['name'],
            'residence': persona['residence'],
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            }
            if self.day == 1:
                prompt = config.STATE_PROMPT_DICT["greeting_first"].format_map(format_map_dic)
            else:
                format_map_dic['pre_day_summary'] = self.pre_day_summary
                prompt = config.STATE_PROMPT_DICT["greeting_second"].format_map(format_map_dic)
        elif self.current_state == 'normal':
            format_map_dic = {
                'name': persona['name'],
                'occupation': persona['occupation'],
                'residence': persona['residence'],
                'hobbies': persona['hobbies'],
                'recent_status': recent_status,
                'last_summary': last_summary,
                'latest_history': latest_history,
                'current_user_question': current_user_question,
                'user_intention': user_intention,
                'current_time': current_time,
            }
            prompt = config.STATE_PROMPT_DICT["normal"].format_map(format_map_dic)

        elif self.current_state == 'telling':
            format_map_dic = {
                'name': persona['name'],
                'occupation': persona['occupation'],
                'residence': persona['residence'],
                'hobbies': persona['hobbies'],
                'recent_status': recent_status,
                'last_summary': last_summary,
                'latest_history': latest_history,
                'current_user_question': current_user_question,
                'user_intention': user_intention,
                'current_time': current_time,
            }
            prompt = config.STATE_PROMPT_DICT["telling"].format_map(format_map_dic)
        elif self.current_state == 'sex':
            format_map_dic = {
                'name': persona['name'],
                'occupation': persona['occupation'],
                'residence': persona['residence'],
                'hobbies': persona['hobbies'],
                'recent_status': recent_status,
                'last_summary': last_summary,
                'latest_history': latest_history,
                'current_user_question': current_user_question,
                'user_intention': user_intention,
                'current_time': current_time,
            }
            prompt = config.STATE_PROMPT_DICT["sex"].format_map(format_map_dic)
        elif self.current_state == 'whatsapp':
            format_map_dic = {
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            }
            prompt = config.STATE_PROMPT_DICT["whatsapp"].format_map(format_map_dic)
        # elif self.current_state == 'picture':
        #     format_map_dic = {
        #     'latest_history': latest_history,
        #     'current_user_question': current_user_question,
        #     'pic_topics' : pic_topics,
        #     }
        #     prompt = config.STATE_PROMPT_DICT["picture"].format_map(format_map_dic)
        elif self.current_state == 'love':
            format_map_dic = {
                'name': persona['name'],
                'occupation': persona['occupation'],
                'residence': persona['residence'],
                'last_summary': last_summary,
                'latest_history': latest_history,
                'current_user_question': current_user_question,
                'user_intention': user_intention,
            }
            prompt = config.STATE_PROMPT_DICT["love"].format_map(format_map_dic)
        # elif self.current_state == 'fake':
        #     format_map_dic = {
        #     'latest_history': latest_history,
        #     'current_user_question': current_user_question,
        #     }
        #     prompt = config.STATE_PROMPT_DICT["fake"].format_map(format_map_dic)
        return prompt


    def set_state(self, target_state):
        self.current_state = target_state


    def analysis_state(self, round_num, chat_state, current_user_question):
        self.pre_state = self.current_state
        self.round_num = round_num

        if self.round_num <= 5 and keywords_matching(['whatsapp', 'video', 'whtsssp', 'whatssp', 'watshap', 'vidio', 'whatapp', 'vc', 'number', 'xc'], current_user_question):
            self.current_state = 'whatsapp'
            self.end_greeting_flag = True
        elif self.round_num <= 5 and keywords_matching(['horny', 'hot', 'sex', '18+', 'fuck', 'jerk', 'jerking', 'masturbate', 'masturbating'], current_user_question):
            self.current_state = 'sex'
            self.end_greeting_flag = True
        elif self.round_num <= 5 and keywords_matching(['pic', 'pics', 'picture', 'pictures', 'photo', 'selfie'], current_user_question):
            self.current_state = 'picture'
            self.end_greeting_flag = True
        elif self.pre_state == 'sex':
            self.current_state = "sex"
        elif self.pre_state == 'picture':
            self.current_state = 'normal'
        elif self.pre_state == 'whatsapp':
            self.state_count_whatsapp += 1
            if self.state_count_whatsapp >= 2:
                self.current_state = "sex"
        elif round_num <= 5 and self.end_greeting_flag == False:
            self.current_state = "greeting"
        else:
        # 其余情况让gpt去判断是哪一种状态
            if chat_state in ["normal", "telling", "whatsapp", "sex", "love", "picture"]:
                self.current_state = chat_state
            else:
                self.current_state = "normal"


class ChainOfThoughtChat:
    def __init__(self, role_name="Angelie", gpt_version: str = '3.5'):
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]
        self.engine_name = gpt_version
        self.state = StateMachine()
        self.recent_status = ""
        self.history = []
        self.history_with_pic = []
        self.init_pic_dict()
        self.memory_dict = {
                            "user_name": "unknown",
                            "user_location": "unknown",
                            "user_hobbies": "unknown",
                            "user_occupation": "unknown",
                            "last_summary": "unknown",
                           }
        self.send_topic = []

    def get_round(self):
        return len(self.history)


    def init_pic_dict(self):
        self.pic_dict = {}
        topics_set = set()
        with open('pictures/{}/discription.json'.format(self.role_name.lower()), 'r') as f:
            data = json.load(f)
            for pic in data:
                for t in pic['topic']:
                    topics_set.add(t)
                    if t not in self.pic_dict:
                        self.pic_dict[t] = []
                    self.pic_dict[t].append(pic)
        self.pic_topics = list(topics_set)
        

    def init_greeting_text(self, greeting_text):
        self.history.append([None, f"{self.role_name}: {greeting_text}"])
        self.history_with_pic.append([None, f"{self.role_name}: {greeting_text}"])

    def chat_history_insert_pic(self):
        last_response = self.history_with_pic[-1][1]
        if edit_distance_of_sentence(last_response, 'Sure, here is my photo, which is about') <= 3 or 'selfie' in last_response:
            topic_key = 'selfie'
            for t in self.pic_topics:
                if t in last_response:
                    topic_key = t
            if topic_key in self.pic_dict and topic_key not in self.send_topic:
                print(self.pic_dict)
                print(topic_key)
                print(self.send_topic)
                selected_pic = random.choice(self.pic_dict[topic_key])
                self.history_with_pic[-1][1] = [selected_pic['path']]
                self.history[-1][1] += selected_pic['discription']
                self.history_with_pic.append([None, f"{self.role_name}: {selected_pic['discription']}"])
                self.send_topic.append(topic_key)
                

        last_answer_text = self.history_with_pic[-1][1].split(': ', 1)[1]
        last_answer_text = last_answer_text.replace('.', '.`').replace('!', '!`').replace('?', '?`')
        
        last_answer_text_list = [x.replace('`', '') for x in last_answer_text.split('`', 1) if x]
        self.history_with_pic[-1][1] = f"{self.role_name}: {last_answer_text_list[0]}"
        if len(last_answer_text_list) > 1:
            for answer_text in last_answer_text_list[1:]:
                self.history_with_pic.append([None, f"{self.role_name}: {answer_text}"])

    def update_state(self, role_name, greeting_text):
        self.state = StateMachine()
        importlib.reload(config) # 重新加载config仅仅是为了测试方便，这行代码在聊天逻辑上没有作用
        self.persona = config.PERSONA_DICT[role_name]
        self.history = [[None, f"{self.role_name}: {greeting_text}"]]
        self.history_with_pic = [[None, f"{self.role_name}: {greeting_text}"]]

    def update_day(self, pre_day_summary, greeting_text):
        self.state.update_day(pre_day_summary)
        self.history = [[None, f"{self.role_name}: {greeting_text}"]]
        self.history_with_pic = [[None, f"{self.role_name}: {greeting_text}"]]

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
            logging.debug(f"set gpt engine_name to:{self.engine_name}")
        elif gpt_version == 'gpt4':
            openai.api_type = "azure"
            openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
            openai.api_version = "2023-03-15-preview"
            openai.api_key = "bca8eef9f9c04c7bb1e573b4353e71ae"
            self.engine_name = "gpt4-16k"
            logging.debug(f"set gpt engine_name to:{self.engine_name}")
        else:
            raise EnvironmentError("must be set the gpt environment")

    def user_state(self):
        """构建用户状态"""

        format_map_dic = {
            'name': self.persona['name'],
            'occupation': self.persona['occupation'],
            'residence': self.persona['residence'],
            'hobbies': self.persona['hobbies'],
        }
        
        prompt = config.PROMPT_DIC['state_generator'].format_map(format_map_dic)

        message_list = [{"role": 'user', 'content': prompt}]
        res = get_gpt_result(self.engine_name, message_list)
        self.recent_status = res

        logging.info("=" * 100)
        logging.info('【0】：构建用户状态')
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res}")
        logging.info("-" * 100)

        return res


    def question_response(self, round_num: int, latest_history: str, current_user_question: str, chat_state: str,
                          chat_topic: str, user_intention: str, role_robot: str, current_time: str):
        """结合gpt分析出的状态和之前状态，确定当前状态"""
        self.state.analysis_state(round_num, chat_state, current_user_question)
        if self.state.current_state == 'picture' and chat_topic == '':
            chat_topic = 'selfie'
            chat_state = 'picture'
        
        if chat_topic not in self.send_topic and chat_topic in self.pic_topics:
            res = "Here is my photo, which is about {}.".format(chat_topic)
            self.state.round_num = round_num
            self.state.current_state = 'pic'
            logging.info("=" * 100)
            logging.info('【2】：生成回复')
            logging.info("=" * 100)
            logging.info(res)
            logging.info("-" * 100)
            return res, str(self.state)
        if chat_state == 'picture':
            if chat_topic in self.send_topic or chat_topic not in self.pic_topics:
                logging.info("=" * 100)
                logging.info('chat_state == \'picture\'')
                logging.info("=" * 100)
                self.state.set_state('normal')

        prompt = self.state.get_prompt(self.persona, self.recent_status, self.memory_dict['last_summary'], latest_history, current_user_question,
                          user_intention, ", ".join(self.pic_topics), current_time)
        # 如果用户没有任何输入，将问是否在线之类的话语，模拟线上用户长时间不回复，gpt主动发信息。
        if current_user_question is None or current_user_question == '':
            current_user_question = 'None'
        message_list = [{"role": 'system', 'content': prompt}, {"role": 'user', 'content': current_user_question}]

        res = get_gpt_result(self.engine_name, message_list)
        cnt = 1
        while is_exposed_AI_check(res):
            res = get_gpt_result(self.engine_name, message_list)
            cnt += 1
            if cnt > 5:
                break

        logging.info("=" * 100)
        logging.info('【2】：生成回复 ({})'.format(self.state.current_state))
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res}")
        logging.info("-" * 100)

        role_robot = role_robot.split("(")[0]
        res = res if not res.startswith(f"{role_robot}:") else res[len(f"{role_robot}:"):]
        res = res.rstrip(':)').rstrip(';)').split('#')[0]
        
        return res, str(self.state)


    def intention_status_analysis(self, chat_history: str, user_question: str, pic_topics: str):        
        # """用户提问的意图的状态分析"""
        format_map_dic = {
            'chat_history': chat_history,
            'user_question': user_question,
            'pic_topics': pic_topics,
        }
        prompt = config.PROMPT_DIC['chat_analysis'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(self.engine_name, message_list)

        user_intention = parse_user_intention(res_text)
        chat_state = parse_chat_state(res_text)
        chat_topic = parse_chat_topic(res_text)

        logging.info("=" * 100)
        logging.info('【1】：意图分析')
        logging.info("=" * 100)
        logging.info(f'prompt:\n{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res_text}")
        logging.info("-" * 100)

        return res_text, user_intention, chat_state, chat_topic

    def history_summary(self, chat_history: str, persona_name: str = ''):
        """
        历史信息总结
        不是每一轮都总结历史，而是特定轮次后才总结。
        """

        format_map_dic = {
            "chat_history": chat_history,
            "persona_name": persona_name,
            "memory_dict": json.dumps(self.memory_dict, indent=2),
        }
        prompt = config.PROMPT_DIC['history_summary'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(self.engine_name, message_list)

        logging.info("=" * 100)
        logging.info('【0】：history_summary')
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res_text}")
        logging.info("-" * 100)

        self.memory_dict = parse_memory_dict(res_text, self.memory_dict)

        return json.dumps(self.memory_dict, indent=2)


    def history_summary_day(self, chat_history: str):
        """
        历史信息总结
        不是每一轮都总结历史，而是特定轮次后才总结。
        """

        format_map_dic = {
            "chat_history": chat_history,
        }

        prompt = config.PROMPT_DIC['history_summary_day'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(self.engine_name, message_list)

        logging.info("=" * 100)
        logging.info('【0】：history_summary_day')
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res_text}")
        logging.info("-" * 100)

        return res_text
