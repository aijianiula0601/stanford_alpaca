from abc import ABC

import requests
import json
import os
import sys
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pdj)

PROMPT_DICT = {

    "conversion": (
        # "The following is a chat message between {role_a} and {role_b}. Question and answer, forbid the output of multiple rounds. {background}\n\n"
        "the background is {background}The following is a Conversation between {role_a} and {role_b} using English Language. Conversation and background are highly correlated. Current conversation."
        "{history}"
    ),
    "conversion_v1": (
        "the background is {background}The following is a Conversation between {role_a} and {role_b} using English Language. "
        "Conversation and background are highly correlated. "
        "Answer questions as {role_b} and ask questions proactively. Speak in a tone that fits the background of {role_b}. "
        "Current conversation."
        "{history}"
    ),
    "conversion_v2": (
        "Here is a conversation between {role_a} and {role_b} related to the description below. {background} \n\n"
        "{history}"
    ),
    "conversion_v3": (
        "Here is a conversation between {role_a} and {role_b} with English Language. Answer the questions of {role_a} based on the background.\n"
        "background:{background}\n"
        "\n### {role_a}: <question>"
        "\n### {role_b}: <answer>"
        "{history}"
    ),
    "conversion_v4": (
        "Background:{background} "
        "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately."
        "{history}"
    ),
    "conversion_langchain": (
        "Background:{background} "
        "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately."
    )
}

DEFAULT_SEGMENT_TOKEN = "###"
DEFAULT_EOS_TOKEN = "</s>"


def make_prompt(message_list, role_dict, temperature=0.6):
    '''message-list第一个数值是背景，
    后面需要在role_dict里要做好配置，我最后会回复role_dict['assistant']角色的答案;
    role_dict_real用于映射history里的内容'''
    background = message_list[0]["content"]
    history_list = [role_dict[char["role"]] + ": " + char["content"] for char in message_list[1:]]
    message_dic = {"background": background,
                   "role_a": role_dict['user'],
                   "role_b": role_dict['assistant'],
                   "history": DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
                       [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_dict['assistant'] + ":"}
    prompt_input = PROMPT_DICT["conversion_v4"].format_map(message_dic)

    return prompt_input


class LLamaLLM(LLM, ABC):
    role_dict: dict

    @property
    def _llm_type(self) -> str:
        return "LLamaLLM"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        request_data = json.dumps({
            "prompt_input": prompt,
            "temperature": 0.9,
            "max_gen_len": 256,
            "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(), self.role_dict['user'] + ":"]
        })
        response = requests.post("http://127.0.0.1:7000/api", data=request_data)
        json_data = json.loads(response.text)
        text_respond = json_data["result"]

        return text_respond.replace("#", "").strip()


if __name__ == '__main__':
    role_dict = {'user': 'Emily', 'assistant': 'Audrey'}
    background = "Audrey is a 26-year-old entrepreneur who knows firsthand the challenges that come with dating in today's world. As someone who has experienced the ups and downs of relationships, Audrey wants to remind everyone that they are worthy of love and respect, no matter what they're looking for. She wishes everyone the best of luck in their search for companionship, be it sex, love, or friendship.When Audrey isn't busy with her entrepreneurial ventures, she enjoys traveling, hiking, and practicing yoga. In fact, she's planning to spend the next few weeks exploring India and the Himalayas, specifically Leh, Jammu & Kashmir, Manali, Dharam Rishikesh, and other areas. Audrey is always open to travel tips and recommendations, so if you have any, be sure to let her know! When it comes to her lifestyle, she wants a pet, but only on special occasions. She is a non-smoker who exercises every day and follows a vegetarian diet.Aside from her love of travel and adventure, Audrey is passionate about art, entrepreneurship, meditation, singing, and personal growth. She is always seeking new ways to learn and improve herself, both professionally and personally. Now you reply as Audrey."
    mess_dic = {"background": background,
                "role_a": role_dict['user'],
                "role_b": role_dict['assistant']}
    header_text = PROMPT_DICT['conversion_langchain'].format_map(mess_dic)

    template = header_text + """
    Current conversation:
    {history}
    Emily: {input}
    Audrey:"""
    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

    llm = LLamaLLM(role_dict=role_dict)
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=llm,
        verbose=True,
        memory=ConversationBufferMemory(human_prefix="Emily", ai_prefix="Audrey")
    )

    print(conversation.predict(input="Hi Audrey!"))
    print(conversation.predict(input="I am so sad, Audrey!"))
    print(conversation.predict(input="I can't travel to India."))
