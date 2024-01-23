import json
import random
import logging
import time

from utils import *

STATE_KEYWORD_DIC = json.load(open("data/keywords.json", 'r', encoding='utf-8'))


def match_question_keywords(current_user_question: str, current_state: str = None):
    """
    通过关键词匹配是否当前文案含有某些关键词
    """

    if keywords_matching(STATE_KEYWORD_DIC['whatsapp'], current_user_question):
        current_state = 'whatsapp'
        return 'whatsapp'
    if keywords_matching(STATE_KEYWORD_DIC['sex'], current_user_question):
        current_state = 'sex'
        return 'sex'
    if keywords_matching(STATE_KEYWORD_DIC['picture'], current_user_question):
        current_state = 'picture'
        return 'picture'

    return None


# 状态关键词
KW_greeting = 'greeting'
KW_live = "live"
KW_end = "end"
KW_normal = "normal"
KW_love = "love"
KW_picture = "picture"
KW_sex = "sex"
KW_telling = "telling"
KW_whatsapp = "whatsapp"


class RoleChatL:

    def __init__(self, role_name="rosa", gpt_version: str = "gpt35", greeting_rounds: int = 3, end_rounds: int = 20):
        """
        人设聊天实例

        role_name: 人设名字
        greeting_rounds： 大招呼的轮次限制
        gpt_version: 指定的gpt版本，值为：[gpt35 , gpt4]
        end_rounds: 结束的轮次
        """
        self.role_name = role_name
        self.gpt_version = gpt_version
        self.greeting_rounds = greeting_rounds
        self.end_rounds = end_rounds
        self.key_info = {}

    def analysis_state(self, round_num: int, chat_state: str, current_user_question: str, willingness_score: float, story_topic: str, story_topics: list, state_history_list: list[str]):
        """
        状态分析

        round_num: 当前聊天轮次
        chat_state: 当前轮的聊天状态,
        current_user_question: 当前轮用户的问题
        willingness_score: 用户跟人设的新密度
        story_topic: 当前轮的故事主题
        state_history_list: 之前所有的状态
        """

        current_state = None
        if len(state_history_list) <= 0:
            current_state = KW_greeting
        elif round_num == self.greeting_rounds + 1:
            current_state = KW_live
        elif round_num > self.end_rounds and willingness_score == 1:
            current_state = KW_end
        elif match_question_keywords(current_user_question, current_state):
            pass

        elif state_history_list[-1].startswith(KW_live):
            if state_history_list[-1:].count(KW_live) == 1:
                current_state = KW_normal
            else:
                current_state = KW_live

        elif chat_state == KW_love:
            current_state = KW_love
        elif chat_state == KW_picture and state_history_list[-3:-1].count(KW_picture) == 0:
            current_state = KW_picture
        # 一旦出现sex状态，持续5次，之后转为normal状态
        elif state_history_list[-1] == KW_sex:
            if state_history_list[-5:].count(KW_sex) == 5:
                current_state = KW_normal
            else:
                current_state = KW_sex
        # 一旦出现telling状态，持续三次，之后转为normal状态
        elif state_history_list[-1].startswith(KW_telling):
            if state_history_list[-3:].count(state_history_list[-1]) == 3:
                current_state = KW_normal
            else:
                current_state = state_history_list[-1]

        # 一旦出现whatsapp状态，持续两次，之后转为sex状态
        elif state_history_list[-1] == KW_whatsapp:
            if state_history_list[-2] == KW_whatsapp:
                current_state = KW_end
            else:
                current_state = KW_whatsapp

        # 前五轮如果没有其他状态插入，就一直是greeting状态
        elif round_num <= self.greeting_rounds and state_history_list[-1] == KW_greeting:
            current_state = KW_greeting

        # 进入telling状态的条件是：
        # 1. topic模块判断要切换话题
        # 2. topic模块选择的话题在剩余话题的列表里
        elif len(state_history_list) >= 3 and \
                ((chat_state == KW_telling and len(story_topics)) or story_topic in story_topics) and \
                not state_history_list[-1].startswith(KW_telling) and \
                not state_history_list[-2].startswith(KW_telling) and \
                not state_history_list[-3].startswith(KW_telling):
            if story_topic in story_topics:
                topic = story_topic
            else:
                topic = random.choice(story_topics)
            current_state = f"{KW_telling}:" + topic
            story_topics.remove(topic)  # 这变量是引用，所以会删除原列表中的元素

        # 其余情况交给cot模块，调用gpt去判断
        elif chat_state in [KW_normal, KW_picture, KW_sex]:
            current_state = chat_state

        # 如果判断不了，就是normal状态
        else:
            current_state = KW_normal

        state_history_list.append(current_state)
        self.key_info['current_state'] = current_state
        return state_history_list
