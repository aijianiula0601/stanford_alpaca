import openai

from abc import ABCMeta, abstractmethod
import config
import random
from openai import OpenAI
"""
def set_gpt_env(gpt_version: str = 3.5):
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
        openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'
        engine_name = "gpt4-16k"
        print(f"set gpt engine_name to:{engine_name}")
    else:
        raise EnvironmentError("must be set the gpt environment")

    return engine_name

def get_gpt_result(message_list: list, engine_name='gpt4') -> str:
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

set_gpt_env(gpt_version="gpt4")
"""

def get_gpt_result(engine_name: str = 'gpt-4', message_list: list = [], api_key='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') -> str:
    api_key = api_key
    client = OpenAI(api_key=api_key, organization='org-vZinLD7D6tNWUWeWJJtAUyzD')

    response = client.chat.completions.create(
        model='gpt-4',
        messages=message_list
    )

    res_text = response.choices[0].message.content
    print("=" * 100)
    print(f"response_text:\n{res_text}")
    print("=" * 100 + "\n\n")
    return res_text


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
    """

    def __init__(self, name: str, gpt_version: str = 'gpt3.5', api_key='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'):
        self.name = name
        self.friend_name = None
        self.engine_name = "gpt-4"#set_gpt_env(gpt_version=gpt_version)
        self.api_key = api_key
        # 每天总结记忆
        self.data_summary_memory_list = []
        # 一天中所有状态的记忆
        self.day_state_memory_list = []

    def get_name(self):
        return self.name

    def pet_info(self):
        """
        获取该宠物描述
        """
        disc_list = []
        for k in config.pets_dic[self.name]:

            if k == "朋友宠物名字":
                self.friend_name = config.pets_dic[self.name][k]
            v = config.pets_dic[self.name][k]
            disc_list.append(f"{k}: {v}")
        disc_str = '\n'.join(disc_list)

        assert self.friend_name is not None, "friend name is None!"

        return disc_str

    def summary_day_state(self):
        """
        总结一天所有的状态
        """

        assert len(self.day_state_memory_list) > 0, "day_state_memory 必须大于1！"
        all_states = '\n'.join(self.day_state_memory_list)
        prompt = config.day_state_summary_prompt.format_map(
            {'role_name': self.name,
             'role_description': self.pet_info(),
             'all_states': all_states,
             })
        print("-" * 100)
        print(f"day plan prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        # 总结完后，情况
        self.day_state_memory_list.clear()
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)

    def day_plan(self, journey_rad: str, destination: str = None, attraction_places: str = None):
        """
        规划一天的行程
        """
        if journey_rad == "出门旅行":
            prompt = config.journey_day_plan_prompt.format_map(
                {'role_name': self.name,
                 'role_description': self.pet_info(),
                 'destination': destination,
                 'destination_places': attraction_places,
                 })
        else:
            prompt = config.day_plan_prompt.format_map(
                {'role_name': self.name,
                 'role_description': self.pet_info(),
                 'all_place': PETWORLD_OBJ.place_str,
                 })

        print("-" * 100)
        print(f"day plan prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)

    def retrieve(self, top_k_m=10):
        """
        取回记忆
        """
        m_list = []
        for m in self.data_summary_memory_list[:top_k_m]:
            m_list.append(m)
        return '\n'.join(m_list)

    def judge_journey_place(self, cur_satiety: str, current_place: str):
        """
        判断旅行位置
        """
        places = ' '.join(config.journey_places)
        prompt = config.judge_journey_place_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(),
             'cur_satiety': cur_satiety, 'current_place': current_place, 'places': places
             })
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)

    def journey_plan(self, sample_destination: str , cur_satiety: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        destination_places_and_description = '\n'.join([f"{p}:{config.attraction_description_dic[p]}" for p in
                                                            config.attraction_dic[sample_destination]])
        destination_places = '\n'.join([p for p in config.attraction_dic[sample_destination]])
        prompt = config.journey_plan_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'cur_satiety': cur_satiety, 
                'destination_places_and_description': destination_places_and_description, 'destination': sample_destination,
                'destination_places': destination_places, 
                })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)

    def get_image_prompt(self, prompt: str, pet_keyword: str):
        """
        判断旅行位置
        """
        prompt = config.img_prompt.format_map(
            {'pet_key_word': pet_keyword, 'jour_disc':prompt})
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name='gpt4', message_list=message_list, api_key=self.api_key)

    def journey_attraction(self, sample_destination: str , cur_satiety: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        prompt = config.judge_attraction_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'cur_satiety': cur_satiety, 
                'jour_place': sample_destination
                })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)
    
    def journey_attraction_gen(self, sample_destination: str , place_arrived: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        prompt = config.judge_attraction_gen_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 
                'jour_place': sample_destination, 'place_arrived':place_arrived,
                })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)
    
    def journey_plan_gen(self, sample_destination: str , place_arrived: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        prompt = config.journey_plan_gen_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 
                'jour_place': sample_destination, 'place_arrived':place_arrived,
                })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)
