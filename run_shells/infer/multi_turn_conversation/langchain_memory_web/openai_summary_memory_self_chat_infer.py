from abc import ABC

import requests
import json
import os
import sys
from typing import Any, List, Mapping, Optional

import openai
from langchain.llms import OpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, CombinedMemory, ConversationSummaryMemory, \
    ConversationSummaryBufferMemory
from langchain.prompts.prompt import PromptTemplate

openai_api_key = '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'

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
    temperature: float

    @property
    def _llm_type(self) -> str:
        return "LLamaLLM"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        request_data = json.dumps({
            "prompt_input": prompt,
            "temperature": self.temperature,
            "max_gen_len": 256,
            "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(), self.role_dict['user'] + ":"]
        })
        response = requests.post("http://127.0.0.1:7000/api", data=request_data)
        json_data = json.loads(response.text)
        text_respond = json_data["result"]

        return text_respond.replace("#", "").strip()


class LLamaMemoryInfer:
    def init(self, background: str, role_dict: dict, max_token_limit: int = 40, temperature: float = 0.9):
        assert 'user' in role_dict and 'assistant' in role_dict
        mess_dic = {"background": background,
                    "role_a": role_dict['user'],
                    "role_b": role_dict['assistant']}
        header_text = PROMPT_DICT['conversion'].format_map(mess_dic)
        template = header_text + "\n" + (
            "Summary of conversation:\n"
            "{history}\n"
            "Current conversation:\n"
            "{human_name}: {input}\n"
            "{bot_name}:").format_map({'history': '{history}',
                                       'input': '{input}',
                                       'human_name': role_dict['user'],
                                       'bot_name': role_dict['assistant']})

        PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

        llm = LLamaLLM(role_dict=role_dict, temperature=temperature)
        self.summary_memory = ConversationSummaryBufferMemory(llm=OpenAI(openai_api_key=openai_api_key),
                                                              max_token_limit=max_token_limit,
                                                              input_key="input",
                                                              human_prefix=role_dict['user'],
                                                              ai_prefix=role_dict['assistant'])
        self.summary_memory.clear()
        self.conversation = ConversationChain(
            llm=llm,
            verbose=True,
            memory=self.summary_memory,
            prompt=PROMPT
        )

    def infer(self, user_input):
        return self.conversation.predict(input=user_input)

    def clear_memory(self):
        self.summary_memory.clear()


if __name__ == '__main__':
    save_f = "/tmp/chat_log.log"
    # ------------------------------------------------------------------------
    # role a
    # ------------------------------------------------------------------------
    role_a_dict = {'user': 'Britney', 'assistant': 'Jack'}
    background_a = 'Jack is a  24 year old man, very wealthy. Jack has a strong desire for control and is allergic to women. Jack is very cold and calculating, very scheming. Jack controls the global economic lifeline. Jack is arrogant and full of himself, never listens to anyone, and thinks that all women in the world will fall in love with him.'

    role_a_llama_memory_infer = LLamaMemoryInfer()
    role_a_llama_memory_infer.init(background_a, role_a_dict, temperature=0.9)

    # ------------------------------------------------------------------------
    # role b
    # ------------------------------------------------------------------------
    role_dict_b = {'user': 'Jack', 'assistant': 'Britney'}
    background_b = "Britney sounds absolutely scandalous, Britney is a married female teacher with fair skin, beautiful appearance and gentle personality. Britney is a natural stunner and is the object of obscenity. Britney is seduced by her boss and other men, and Britney is involved in a The promiscuous life, the orgasms made him lose himself again and again, Britney enjoyed this feeling more and more, and enjoyed having sex with different men every day. Britney can't help but start to writhe when Britney sees a man's dick now, ready get fucked. Britney is talkative, always speak a lot in conversion."
    role_b_llama_memory_infer = LLamaMemoryInfer()
    role_b_llama_memory_infer.init(background_b, role_dict_b, temperature=0.9)

    # ------------------------------------------------------------------------
    # 生成互相对话
    # ------------------------------------------------------------------------
    with open(save_f, 'a', buffering=1) as fw:
        fw.write("=" * 100 + "\n")
        fw.write("=" * 100 + "\n")
        britney_question = "hi, Jack. how do you do?"
        fw.write(f"Britney: {britney_question}\n")
        print(f"Britney: {britney_question}")
        for _ in range(20):
            jack_question = role_a_llama_memory_infer.infer(user_input=britney_question)
            fw.write(f"Jack: {jack_question}\n")
            fw.write("-" * 100 + "\n")
            print("Jack:", jack_question)
            print("-" * 100)
            britney_question = role_b_llama_memory_infer.infer(user_input=jack_question)
            print("Britney:", britney_question)
            fw.write(f"Britney: {britney_question}\n")
    print("=" * 100)
    print("=" * 100)
