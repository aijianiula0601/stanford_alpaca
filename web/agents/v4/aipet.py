import openai

from abc import ABCMeta, abstractmethod
import config
import random


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
    """

    def __init__(self, name: str, gpt_version: str = 'gpt3.5'):
        self.name = name
        self.friend_name = None
        self.engine_name = set_gpt_env(gpt_version)
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
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

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
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def retrieve(self, top_k_m=10):
        """
        取回记忆
        """
        m_list = []
        for m in self.data_summary_memory_list[:top_k_m]:
            m_list.append(m)
        return '\n'.join(m_list)

    def state(self, curr_time: str, next_time: str, day_plan: str, cur_state: str, cur_satiety: str,
              friend_cur_state: str = None,
              journey_rad: str = None, destination: str = None):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """

        if journey_rad == "出门旅行":
            destination_places_and_description = '\n'.join([f"{p}:{config.attraction_description_dic[p]}" for p in
                                                            config.attraction_dic[destination]])
            place2img = '\n'.join([f"{p}:{config.attraction_path_dic[p]}" for p in config.attraction_dic[destination]])

            prompt = config.journey_state_prompt.format_map(
                {'role_name': self.name, 'role_description': self.pet_info(), 'all_place': PETWORLD_OBJ.place_str,
                 'curr_time': curr_time, 'day_plan': day_plan, 'cur_state': cur_state,
                 'next_time': next_time, 'friend_name': self.friend_name, 'friend_cur_state': friend_cur_state,
                 'journey_rad': journey_rad, 'cur_satiety': cur_satiety,
                 'destination_places_and_description': destination_places_and_description, 'destination': destination,
                 'place2img': place2img
                 })
        else:
            prompt = config.state_prompt.format_map(
                {'role_name': self.name, 'role_description': self.pet_info(), 'all_place': PETWORLD_OBJ.place_str,
                 'curr_time': curr_time, 'day_plan': day_plan, 'cur_state': cur_state,
                 'next_time': next_time, 'friend_name': self.friend_name, 'friend_cur_state': friend_cur_state,
                 'journey_rad': journey_rad, 'cur_satiety': cur_satiety,
                 })
        print("-" * 100)
        print(f"state prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def judge_journey_place(self, curr_time: str, next_time: str, current_state: str, feed_type: str):
        """
        判断旅行位置
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

    def stroke(self, curr_time: str, current_state: str, stroke_type: str, next_time: str, day_plan: str):
        """
        主人抚摸
        """

        stroke_type2img_path = "\n".join([f"{k}: {config.cat_actor_dic[k]}" for k in config.cat_actor_dic.keys()])
        all_actors = ",".join(list(config.cat_actor_dic.keys()))

        prompt = config.stroke_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'all_place': PETWORLD_OBJ.place_str, 'stroke_type2img_path': stroke_type2img_path,
             'all_actors': all_actors,
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

    ##################
    # 旅行
    ##################

    def place_decide(self, curr_time: str, current_state: str):

        places = ' '.join([place for place in config.journey_places])
        prompt = config.place_decide_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'current_state': current_state, 'places': places
             })
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def attraction_decide(self, place, curr_time: str, current_state: str):
        for pla in config.journey_places:
            if pla in place:
                place = pla
        attractions = ' '.join([attraction for attraction in config.attraction_dic[place]])
        prompt = config.attraction_decide_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'current_state': current_state, 'places': attractions
             })
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list)

    def attraction_travel(self, place, attraction, curr_time: str, current_state: str):

        for att in config.attraction_dic[place]:
            if att in attraction:
                attraction = att
        prompt = config.attraction_travel_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(), 'curr_time': curr_time,
             'current_state': current_state, 'attraction': attraction,
             'discreption': config.attraction_description_dic[attraction]
             })
        print("-" * 100)
        print(f"give_feed prompt:\n{prompt}")
        print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        path = config.attraction_path_dic[attraction]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list), path
