import json
import openai
import re
import time
import config
import copy
from numpy import dot
from numpy.linalg import norm


def get_gpt_result(engine_name: str, message_list: list):
    if engine_name == 'gpt4-16k':
        openai.api_type = "azure"
        openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
        openai.api_version = "2023-03-15-preview"
        openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'
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


def get_response(prompt=None, content=None):
    key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

    openai.api_type = "azure"
    openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

    message_list = [
        {"role": "system",
         "content": f"{content}"},
        {"role": "user", "content": f"{prompt}"}
    ]
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


def get_embedding(text, model="text-embedding-ada-002"):
    openai_api_key = "548e5c0c2aff453e932948927a27bde6"
    openai.api_key = openai_api_key
    openai.api_type = "azure"
    # openai.api_version = "2023-06-15-preview"
    openai.api_version = "2023-03-15-preview"
    openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
    res = openai.Embedding.create(
        input=[text], deployment_id="text-embedding-ada-002")['data'][0]['embedding']
    return res


### 定义匹配函数，对于每个当下接收到的信息 perceived，将perceived每个事件的embedding与过往事件的embedding做向量匹配
### 匹配方式是余弦相似度，每个perceived事件返回最高的两个过往事件
def get_revelant_past_mem(perceived, prev_mem, top_k=2):
    sim_score = [[0 for _ in range(len(prev_mem))] for _ in range(len(perceived))]
    relevent_idx = {}
    perceived_emb = [get_embedding(perceived[i]) for i in range(len(perceived))]
    prev_mem_emb = [get_embedding(prev_mem[i]) for i in range(len(prev_mem))]
    for i in range(len(perceived)):
        for j in range(len(prev_mem)):
            sim_score[i][j] = cos_sim(perceived_emb[i], prev_mem_emb[j])
        relevent_idx[i], _ = get_top_k_idx(sim_score[i])
    return relevent_idx, perceived_emb, prev_mem_emb


def cos_sim(a, b):
    ## 返回一个值 0-1
    return dot(a, b) / (norm(a) * norm(b))


def get_top_k_idx(scores, top_k=2):
    t = copy.deepcopy(scores)
    # 求m个最大的数值及其索引
    max_number = []
    max_index = []
    for _ in range(top_k):
        number = max(t)
        index = t.index(number)
        t[index] = 0
        max_number.append(number)
        max_index.append(index)
    return max_index, max_number


def add_prev_mem(moli, bobo):
    for mem in config.prev_mem_moli:
        moli.add_memory(mem)
    for mem in config.prev_mem_bobo:
        bobo.add_memory(mem)


def pets_chat(pet1, pet2, state1, state2, foc_mem1, foc_mem2, act_place):
    """
    规划一天的行程
    """
    prompt = config.chat_pets_prompt.format_map(
        {'pet1_info': pet1.pet_info(),
         'pet2_info': pet2.pet_info(),
         'pet1_state': state1,
         'pet2_state': state2,
         'pet1_foc_mem': foc_mem1,
         'pet2_foc_mem': foc_mem2,
         'act_place': act_place
         })
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(engine_name=pet1.engine_name, message_list=message_list)


class PetWorld:
    def __init__(self):
        self.place_str = self.location_entities()

    def location_entities(self):
        """
        获取可活动的位置
        """
        place_list = []
        for k in config.places_dic:
            text = config.places_dic[k]
            place_list.append(f"{k}: {text}")

        return '-' + '\n-'.join(place_list)

    def pets(self):
        """
        所有宠物介绍
        """
        pets_description_list = []
        for pet_name in config.pets_dic:
            disc_list = []
            for k in config.pets_dic[pet_name]:
                v = config.pets_dic[pet_name][k]
                disc_list.append(f"{k}: {v}")

            disc_str = '\n'.join(disc_list)
            pets_description_list.append(f"{pet_name}:\n{disc_str}")

        pets_names = list(config.pets_dic.keys())
        return pets_names, pets_description_list


PETWORLD_OBJ = PetWorld()


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
    def __init__(self, role_name="Rabit(pet)", gpt_version: str = 'gpt3.5'):
        self.full_message_history = []
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]
        self.engine_name = gpt_version
        self.memory_list = config.PERSONA_DICT[role_name]['记忆']
        self.set_gpt_env(gpt_version)

    def pet_info(self):
        """
        获取该宠物的名字、介绍
        """
        disc_list = []
        for k in config.PERSONA_DICT[self.role_name]:
            if '记忆' == k:
                continue
            v = config.PERSONA_DICT[self.role_name][k]
            disc_list.append(f"{k}: {v}")
        disc_str = '\n'.join(disc_list)

        return disc_str

    def update_state(self):
        # self.state = StateMachine()
        pass

    def set_role(self, role_name):
        self.role_name = role_name
        self.persona = config.PERSONA_DICT[role_name]

    def set_gpt_env(self, gpt_version: str = "gpt3.5"):
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
            openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'
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
            'food_like': self.persona['food_like'],
            'touch_like': self.persona['touch_like'],
            'now_work': now_work,
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            'touch_type': touch_type,
            'food_type': food_type,

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
        """当前状态分析"""

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

        # 饱食度、心情、现在工作、今日总结
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

    def add_memory(self, observation: str):
        """
        添加记忆事件
        """
        self.memory_list.append(observation)

    def decide_act_place(self, current_state):
        """
        计划要去的地方
        """
        prompt = config.decide_act_place_prompt.format_map(
            {'role_name': self.role_name,
             'role_description': self.pet_info(),
             'all_place': PETWORLD_OBJ.place_str,
             'current_state': current_state,
             })
        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(engine_name=self.engine_name, message_list=message_list)
        # next_plan, next_place = parse_intention_state(res_text, '下一步计划'), parse_intention_state(res_text, '准备活动的位置')
        next_place = parse_intention_state(res_text, '准备活动的位置')
        return next_place

    def get_focused_env(self, act_place, current_state):
        # perceived = "你现在正在：" + act_place + "\n" + "你现在正在做的事是：\n" + current_state
        # perceived = [perceived]
        # reterived_mem_dic, _, _ = get_revelant_past_mem(perceived=perceived, prev_mem=self.memory_list)
        # reterived_mem_idx = []
        # for k in reterived_mem_dic.keys():
        #     for i in range(len(reterived_mem_dic[k])):
        #         if reterived_mem_dic[k][i] not in reterived_mem_idx:
        #             reterived_mem_idx.append(reterived_mem_dic[k][i])
        # focused_event = [self.memory_list[reterived_mem_idx[i]] for i in range(len(reterived_mem_idx))]

        # 直接拿出所有的记忆
        focused_event = '\n'.join(self.memory_list[:20])

        return focused_event

    def decide_chat_plan(self, current_state, scenario, scenario_frind, focused_mem, pet_friend, friend_current):
        """
        规划一天的行程
        """
        prompt = config.chat_decide_prompt.format_map(
            {'role_name': self.role_name,
             'role_description': self.pet_info(),
             'current_state': current_state,
             'scenario': scenario,
             'scenario_frind': scenario_frind,
             'focused_mem': focused_mem,
             'pet_friend': pet_friend,
             'friend_current': friend_current
             })
        """
        print("-" * 100)
        print(f"act place prompt:\n{prompt}")
        print("-" * 100)"""
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def act_plan(self, act_place: str, current_state: str, memory_env: str, friend_state: str, friend_name: str):
        """
        根据初始状态、近期状态、记忆 以后的计划
        """
        prompt = config.act_plan_prompt.format_map(
            {'role_name': self.role_name,
             'role_description': self.pet_info(),
             'act_place': act_place,
             'memory_env': memory_env,
             'friend_state': friend_state,
             'friend_name': friend_name,
             'current_state': current_state,
             })

        print("-" * 100)
        print("act plan:", prompt)
        print("-" * 100)

        message_list = [{"role": "user", "content": prompt}]
        res_text = get_gpt_result(engine_name=self.engine_name, message_list=message_list)

        next_plan = parse_intention_state(res_text, '下一步计划')
        next_plan_place = parse_intention_state(res_text, '下一步计划的位置')

        return next_plan, next_plan_place

    def new_state(self, next_plan_place: str, next_plan: str, friend_next_plan: str, friend_name: str):
        """
        根据初始状态、近期状态、记忆 以后的计划
        """
        prompt = config.new_state_prompt.format_map(
            {'role_name': self.role_name,
             'role_description': self.pet_info(),
             'act_place': next_plan_place,
             'friend_next_plan': friend_next_plan,
             'friend_name': friend_name,
             'plan': next_plan,
             })
        """
        print("-" * 100)
        print(f"plan prompt:\n{prompt}")
        print("-" * 100)"""
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def doing_evn(self, current_state: str):
        """
        现在做什么
        """
        prompt = config.doing_prompt.format_map(
            {'role_name': self.role_name,
             'role_description': self.pet_info(),
             'current_state': current_state,
             })
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)


def init_two_pets():
    moli = PetChat(role_name="莫莉", gpt_version="4")
    bobo = PetChat(role_name="波波", gpt_version="4")
    moli.set_gpt_env('gpt4')
    bobo.set_gpt_env('gpt4')

    moli.current = "莫莉正在看电视"
    bobo.current = "波波正在喝咖啡"

    moli.act_place = moli.decide_act_place(moli.current)
    bobo.act_place = bobo.decide_act_place(bobo.current)

    moli.focused_env = moli.get_focused_env(moli.act_place, moli.current)
    bobo.focused_env = bobo.get_focused_env(bobo.act_place, bobo.current)

    return moli, bobo


if __name__ == '__main__':
    moli, bobo = init_two_pets()


    def run_two_pets_act(moli=moli, bobo=bobo):
        print('-' * 100)
        chat_deci_moli = moli.decide_chat_plan(current_state=moli.current, scenario=moli.act_place,
                                               focused_mem=moli.focused_env, pet_friend='波波',
                                               friend_current=bobo.current)
        chat_deci_bobo = moli.decide_chat_plan(current_state=bobo.current, scenario=bobo.act_place,
                                               focused_mem=bobo.focused_env, pet_friend='莫莉',
                                               friend_current=moli.current)
        print('-' * 100)
        print('moli:' + chat_deci_moli + '                bobo' + chat_deci_bobo)
        if '1' in chat_deci_moli and '1' in chat_deci_bobo:
            chat_content = pets_chat(pet1=moli, pet2=bobo, state1=moli.current, state2=bobo.current,
                                     foc_mem1=moli.focused_env, foc_mem2=bobo.focused_env, act_place=moli.act_place)
            print('-' * 100)
            print("+++++++++++++++++++      开始聊天    +++++++++++++++++++++++++++++++")
            print(chat_content)
            message_list = [{"role": "user", "content": config.get_summarized_chat.format_map({'chat': chat_content})}]
            summarized_chat = get_gpt_result(engine_name=moli.engine_name, message_list=message_list)
            moli.memory_list.append(summarized_chat)
            bobo.memory_list.append(summarized_chat)
            moli.current = "刚刚结束一段关于：\n" + summarized_chat + "\n 的对话"
            bobo.current = "刚刚结束一段关于：\n" + summarized_chat + "\n 的对话"
            ## 更新状态
            moli.act_place = moli.decide_act_place(moli.current)
            bobo.act_place = bobo.decide_act_place(bobo.current)
            moli.focused_env = moli.get_focused_env(moli.act_place, moli.current)
            bobo.focused_env = bobo.get_focused_env(bobo.act_place, bobo.current)
        else:
            plan_moli = moli.act_plan(act_place=moli.act_place, current_state=moli.current)
            plan_bobo = bobo.act_plan(act_place=bobo.act_place, current_state=bobo.current)
            print('-' * 100)
            print("+++++++++++++++++++      制定的计划    +++++++++++++++++++++++++++++++")
            print(plan_moli)
            print(plan_bobo)
            moli.current = moli.new_state(next_plan_place=moli.act_place, next_plan=plan_moli)
            bobo.current = bobo.new_state(next_plan_place=bobo.act_place, next_plan=plan_bobo)
            print("+++++++++++++++++++      当前的状态    +++++++++++++++++++++++++++++++")
            print(moli.current)
            print(bobo.current)
            moli.memory_list.append(plan_moli)
            bobo.memory_list.append(plan_bobo)
            moli.act_place = moli.decide_act_place(moli.current)
            bobo.act_place = bobo.decide_act_place(bobo.current)
            moli.focused_env = moli.get_focused_env(moli.act_place, moli.current)
            bobo.focused_env = bobo.get_focused_env(bobo.act_place, bobo.current)
