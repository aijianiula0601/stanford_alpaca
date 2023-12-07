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


def get_gpt_result(engine_name: str = 'gpt-4', message_list: list = [],
                   api_key='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') -> str:
    api_key = api_key
    client = OpenAI(api_key=api_key, organization='org-vZinLD7D6tNWUWeWJJtAUyzD')

    response = client.chat.completions.create(
        model='gpt-4',
        messages=message_list
    )

    res_text = response.choices[0].message.content
    # print("=" * 100)
    # print(f"response_text:\n{res_text}")
    # print("=" * 100 + "\n\n")
    return res_text


class PersonPet:
    """
    ai宠物实例
    """

    def __init__(self, name: str, gpt_version: str = 'gpt3.5',
                 api_key='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'):
        self.name = name
        self.friend_name = None
        self.engine_name = "gpt-4"  # set_gpt_env(gpt_version=gpt_version)
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

    def get_image_prompt(self, prompt: str, pet_keyword: str):
        """
        判断旅行位置
        """
        prompt = config.img_prompt.format_map(
            {'pet_key_word': pet_keyword, 'jour_disc': prompt})
        # print("-" * 100)
        # print(f"give_feed prompt:\n{prompt}")
        # print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name='gpt4', message_list=message_list, api_key=self.api_key)

    def journey_plan_gen(self, sample_destination: str, place_arrived: str):
        """
        获取宠物当前状态：心情、饱腹感、思考，当前在干什么
        """
        prompt = config.journey_plan_gen_prompt.format_map(
            {'role_name': self.name, 'role_description': self.pet_info(),
             'jour_place': sample_destination, 'place_arrived': place_arrived,
             })
        # print("-" * 100)
        # print(f"state prompt:\n{prompt}")
        # print("-" * 100)
        message_list = [{"role": "user", "content": prompt}]
        return get_gpt_result(engine_name=self.engine_name, message_list=message_list, api_key=self.api_key)
