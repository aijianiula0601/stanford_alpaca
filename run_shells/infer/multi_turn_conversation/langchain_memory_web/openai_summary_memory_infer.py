from abc import ABC

import requests
import json
import os
import sys
from typing import Any, List, Mapping, Optional

from langchain.llms import OpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, CombinedMemory, ConversationSummaryMemory, \
    ConversationSummaryBufferMemory
from langchain.prompts.prompt import PromptTemplate

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pdj)

PROMPT_DICT = {
    "conversion": (
        "Background:{background} "
        "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately."
    )
}

DEFAULT_SEGMENT_TOKEN = "###"
DEFAULT_EOS_TOKEN = "</s>"


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
    header_text = PROMPT_DICT['conversion'].format_map(mess_dic)

    template = header_text + """
    Summary of conversation:
    {history}
    Current conversation:
    {human_name}: {input}
    {bot_name}:""".format_map(
        {'history': '{history}',
         'input': '{input}',
         'human_name': role_dict['user'],
         'bot_name': role_dict['assistant']})
    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

    llm = LLamaLLM(role_dict=role_dict)

    # summary_memory = ConversationSummaryMemory(llm=OpenAI(), input_key="input", human_prefix="Emily", ai_prefix="Audrey")
    summary_memory = ConversationSummaryBufferMemory(llm=OpenAI(), max_token_limit=40, input_key="input",
                                                     human_prefix=role_dict['user'], ai_prefix=role_dict['assistant'])

    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=summary_memory,
        prompt=PROMPT
    )

    print(conversation.predict(input="Hi Audrey!"))
    print('-' * 100)
    print(conversation.predict(input="I am so sad, Audrey!"))
    print('-' * 100)
    print(conversation.predict(input="I can't travel to India."))
    print('-' * 100)
    print(conversation.predict(input="Are you going on a trip?"))
    print('-' * 100)
    print(conversation.predict(input="When are you going to go? How can I get there?"))
