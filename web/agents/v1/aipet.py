import openai

from abc import ABCMeta, abstractmethod
import config


def get_gpt_result(engine_name: str, message_list: list) -> str:
    response = openai.ChatCompletion.create(
        engine=engine_name,
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    res_text = response['choices'][0]['message']['content']
    print("=" * 100)
    print(f"response_text:\n{res_text}")
    print("=" * 100 + "\n\n")
    return res_text


def set_gpt_env(gpt_version: str = 3.5):
    """设置gpt接口类型，3.5还是4"""
    if gpt_version == "gpt3.5":
        openai.api_type = "azure"
        openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
        openai.api_version = "2023-03-15-preview"
        openai.api_key = "0ea6b47ac9e3423cab22106d4db65d9d"
        engine_name = "bigo-gpt35"
        print(f"set gpt engine_name to:{engine_name}")
    elif gpt_version == 'gpt4':
        openai.api_type = "azure"
        openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
        openai.api_version = "2023-03-15-preview"
        openai.api_key = "bca8eef9f9c04c7bb1e573b4353e71ae"
        engine_name = "gpt4-16k"
        print(f"set gpt engine_name to:{engine_name}")
    else:
        raise EnvironmentError("must be set the gpt environment")

    return engine_name


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


class AiPet(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self):
        pass


class ConversationMemory:
    """
    用户保存聊天记录
    """

    def __init__(self, chat_to_pet: AiPet, limit_c=10):
        """
        chat_to_pet: 聊天对象
        """
        self.chat_to_pet = chat_to_pet
        self.limit_c = limit_c
        self.conversation_history_list = []

    def add_one_chat(self, chat_obj={}):
        """
        添加一次聊天记录
        {'name': '~', 'text': '~'}
        """
        if len(self.conversation_history_list) > self.limit_c:
            self.conversation_history_list.pop()

        self.conversation_history_list.append(chat_obj)

    def get_conversation_history(self):

        history_list = []
        for c in self.conversation_history_list:
            history_list.append(f"{c['name']}: {c['text']}")

        return '\n'.join(history_list)


class PersonPet(AiPet):
    """
    ai宠物实例
    宠物状态的执行步骤应该是：
    1、plan
    2、retrieve
    3、actor
    """

    def __init__(self, name: str, gpt_version: str = 'gpt3.5'):
        self.name = name

        self.memory_list = []
        self.conversation_memory = None
        self.engine_name = set_gpt_env(gpt_version)
        self.state_memory = []

    def get_name(self):
        return self.name

    def pet_info(self):
        """
        获取该宠物的名字、介绍
        """
        disc_list = []
        for k in config.pets_dic[self.name]:
            v = config.pets_dic[self.name][k]
            disc_list.append(f"{k}: {v}")
        disc_str = '\n'.join(disc_list)

        return disc_str

    def add_memory(self, observation: str):
        """
        添加记忆事件
        """
        self.memory_list.append(observation)

    def user_pet_chat(self, curr_time: str, current_state: str, user_question: str, pet_question: str,
                      conversation_history_str: str, your_plans: str):
        """
        主人和宠物的聊天(宠物主动找主人来聊天，主人主动找宠物可能还不需要---开会说的)
        """

        prompt = config.chat_prompt.format_map(
            {'role_name': self.name,
             'role_description': self.pet_info(),
             'all_place': PETWORLD_OBJ.place_str,
             'your_plans': your_plans,
             'curr_time': curr_time,
             'current_state': current_state,
             'conversation_history': conversation_history_str,
             'user_question': user_question,
             'pet_question': pet_question,

             })
        print("-" * 100)
        print(f"plan prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]

        res = get_gpt_result(engine_name=self.engine_name, message_list=message_list)

        if res.startswith(f"{self.name}:") or res.startswith(f"{self.name}："):
            return res.replace(f"{self.name}:", "").strip()

        if res.startswith(f"{self.name}："):
            return res.replace(f"{self.name}：", "").strip()

        return res

    def plan(self, current_state: str, curr_time: str):
        """
        根据初始状态、近期状态、记忆 以后的计划
        """
        prompt = config.plan_prompt.format_map(
            {'role_name': self.name,
             'role_description': self.pet_info(),
             'all_place': PETWORLD_OBJ.place_str,
             'current_state': current_state,
             'curr_time': curr_time
             })
        print("-" * 100)
        print(f"plan prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def day_plan(self):
        """
        规划一天的行程
        """
        prompt = config.day_plan_prompt.format_map(
            {'role_name': self.name,
             'role_description': self.pet_info(),
             'all_place': PETWORLD_OBJ.place_str,
             })
        print("-" * 100)
        print(f"day plan prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def retrieve(self, top_k_m=10):
        """
        取回记忆
        """
        m_list = []
        for m in self.memory_list[:top_k_m]:
            m_list.append(m)
        return '\n'.join(m_list)

    # def actor(self, cur_plan: str, current_state: str):
    #     """
    #     根据当前状态、计划、近期记忆 做出下一步的动作
    #     """
    #     prompt = config.actor_prompt.format_map(
    #         {'role_name': self.name, 'role_description': self.pet_info(), 'all_place': PETWORLD_OBJ.place_str,
    #          'your_plans': cur_plan,
    #          'current_state': current_state})
    #     print("-" * 100)
    #     print(f"actor prompt:\n{prompt}")
    #     print("-" * 100)
    #     message_list = [{"role": "user", "content": prompt}]
    #     return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def save_state(self, cur_state: str):
        """
        状态记忆
        """
        self.state_memory.append(cur_state)

    def get_state(self):
        """
        获取状态记忆
        """
        return "\n".join(self.state_memory)

    def state(self, curr_time: str, next_time: str, day_plan: str, cur_state: str, conversation_history: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        prompt = config.state_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'all_place': PETWORLD_OBJ.place_str,
             'curr_time': curr_time, 'day_plan': day_plan, 'cur_state': cur_state,
             'conversation_history': conversation_history,
             'next_time': next_time
             })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def push(self, curr_time: str, current_state: str):
        """
        推送信息
        """
        prompt = config.push_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'current_state': current_state,
             'curr_time': curr_time
             })
        print("-" * 100)
        print(f"push prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def leave_message(self, curr_time: str, current_state: str):
        """
        给主人留言的信息
        """
        prompt = config.leave_message_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'current_state': current_state,
             'curr_time': curr_time
             })
        print("-" * 100)
        print(f"leave_message prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def give_feed(self, curr_time: str, next_time: str, current_state: str, feed_type: str):
        """
        投喂食物
        """
        prompt = config.give_feed_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'current_state': current_state, 'feed_type': feed_type, 'next_time': next_time
             })
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def summon(self, curr_time: str, next_time: str, current_state: str):
        """
        主人召唤了
        """
        prompt = config.summon_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'all_place': PETWORLD_OBJ.place_str,
             'current_state': current_state, "next_time": next_time
             })
        print("-" * 100)
        print(f"summon prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]

        res = get_gpt_result(engine_name=self.engine_name, message_list=message_list)
        if res.startswith(f"{self.name}:") or res.startswith(f"{self.name}："):
            return res.replace(f"{self.name}:", "").strip()
        return res

    def stroke(self, curr_time: str, current_state: str, stroke_type: str, next_time: str, day_plan: str):
        """
        主人抚摸
        """
        prompt = config.stroke_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'all_place': PETWORLD_OBJ.place_str,
             'current_state': current_state, "stroke_type": stroke_type, 'next_time': next_time, 'day_plan': day_plan,
             })
        print("-" * 100)
        print(f"stroke prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]

        res = get_gpt_result(engine_name=self.engine_name, message_list=message_list)
        if res.startswith(f"{self.name}:") or res.startswith(f"{self.name}："):
            return res.replace(f"{self.name}:", "").strip()
        return res


if __name__ == '__main__':
    pp = PersonPet(name="莫莉", gpt_version="gpt3.5")
    cur_plan = pp.plan()
    print("-" * 100)
    print(cur_plan)
    print("-" * 100)

    curr_time = "11:30:00"
    current_status = pp.state(curr_time)
    print("current_status:\n", current_status)

    print("-" * 100)
    cur_actor = pp.actor(cur_plan, current_status)
    print("cur_actor:\n", cur_actor)
    print("-" * 100)

    cur_push = pp.push(curr_time, current_status)
    print('cur_psh:', cur_push)
    print('-' * 100)
