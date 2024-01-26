import json
import random
import logging
import time

from utils import *
from get_prompts import *

STATE_KEYWORD_DIC = json.load(open("data/keywords.json", 'r', encoding='utf-8'))


def match_question_keywords(current_state, current_user_question: str):
    """
    通过关键词匹配是否当前文案含有某些关键词
    """
    current_state = None
    if keywords_matching(STATE_KEYWORD_DIC['whatsapp'], current_user_question):
        current_state = 'whatsapp'
    elif keywords_matching(STATE_KEYWORD_DIC['sex'], current_user_question):
        current_state = 'sex'
    elif keywords_matching(STATE_KEYWORD_DIC['picture'], current_user_question):
        current_state = 'picture'

    return current_state


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

    def state_verify(self, round_num: int, chat_state: str, current_user_question: str, willingness_score: float, story_topic: str, story_topics: list, state_history_list: list[str]):
        """
        状态确认

        round_num: 当前聊天轮次
        chat_state: 当前轮的聊天状态,
        current_user_question: 当前轮用户的问题
        willingness_score: 用户跟人设的亲密度
        story_topic: 当前轮的故事主题
        state_history_list: 之前所有的状态
        """

        current_state = None
        # ----------------------------------------------
        # 开始优化状态【greeting】
        # ----------------------------------------------
        if len(state_history_list) <= 0:
            current_state = KW_greeting
        # ----------------------------------------------
        # 友好状态超过指定轮次，转【live】状态
        # ----------------------------------------------
        elif round_num == self.greeting_rounds + 1:
            current_state = KW_live

        # ----------------------------------------------
        # 到达限定的指定轮次，转【end】状态
        # ----------------------------------------------
        elif round_num > self.end_rounds and willingness_score == 1:
            current_state = KW_end

        # ----------------------------------------------
        # 根据用户问题，转到【whatsapp】|【sex】|【picture】中
        # 某个状态
        # ----------------------------------------------
        elif match_question_keywords(current_state, current_user_question):
            pass

        # ----------------------------------------------
        # 如果最后一个状态为：live，转为【live】或者【normal】
        # ----------------------------------------------
        elif state_history_list[-1].startswith(KW_live):
            if state_history_list[-1:].count(KW_live) == 1:
                current_state = KW_normal
            else:
                current_state = KW_live
        # ----------------------------------------------
        # 如果聊天状态为：love，转【love】
        # ----------------------------------------------
        elif chat_state == KW_love:
            current_state = KW_love
        # ----------------------------------------------
        # 如果聊天状态为：picture并且前三个状态中没有picture
        # 状态，转为【picture】
        # ----------------------------------------------
        elif chat_state == KW_picture and state_history_list[-3:-1].count(KW_picture) == 0:
            current_state = KW_picture
        # ----------------------------------------------
        # 一旦出现sex状态，持续5次，之后转为【normal】状态
        # ----------------------------------------------
        elif state_history_list[-1] == KW_sex:
            if state_history_list[-5:].count(KW_sex) == 5:
                current_state = KW_normal
            else:
                current_state = KW_sex
        # ----------------------------------------------
        # 一旦出现telling状态，持续三次，之后转为【normal】状态
        # ----------------------------------------------
        elif state_history_list[-1].startswith(KW_telling):
            if state_history_list[-3:].count(state_history_list[-1]) == 3:
                current_state = KW_normal
            else:
                current_state = state_history_list[-1]

        # ----------------------------------------------
        # 一旦出现whatsapp状态，持续两次，之后转为【sex】状态
        # ----------------------------------------------
        elif state_history_list[-1] == KW_whatsapp:
            if state_history_list[-2] == KW_whatsapp:
                current_state = KW_end
            else:
                current_state = KW_whatsapp

        # ----------------------------------------------
        # 前五轮如果没有其他状态插入，就一直是【greeting】状态
        # ----------------------------------------------
        elif round_num <= self.greeting_rounds and state_history_list[-1] == KW_greeting:
            current_state = KW_greeting

        # ----------------------------------------------
        # 进入telling状态的条件是：
        # 1. topic模块判断要切换话题
        # 2. topic模块选择的话题在剩余话题的列表里
        # ----------------------------------------------
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

        # ----------------------------------------------
        # 其余情况交给cot模块，调用gpt去判断
        # ----------------------------------------------
        elif chat_state in [KW_normal, KW_picture, KW_sex]:
            current_state = chat_state

        # ----------------------------------------------
        # 如果判断不了，就是【normal】状态
        # ----------------------------------------------
        else:
            current_state = KW_normal

        state_history_list.append(current_state)

        return state_history_list

    def get_state_result(self,
                         persona: dict,
                         latest_history: str,
                         current_user_question: str,
                         user_intention: str,
                         current_time: str,
                         chat_day: int,
                         state_history: list,
                         pre_day_summary: str):
        """
        当前状态根据prompt获取结果

        persona: 人设信息
        latest_history: 最新的几轮聊天历史
        current_user_question: 当前用户的回复
        user_intention: 当初用户回复的意图
        current_time: 当前时间
        story_topic: 故事主题
        story_topics: 故事主题list
        chat_day: 当前的聊天是第几天了
        state_history: 状态历史列表
        pre_day_summary
        """
        current_state = state_history[-1]
        if current_state == KW_greeting:
            if chat_day == 1:
                return get_result_from_prompt_greeting_first_day(role_name=persona['name'], residence=persona['residence'], latest_history=latest_history, current_user_question=current_user_question)
            else:
                return get_result_from_prompt_greeting_second_day(role_name=persona['name'], residence=persona['residence'], yesterday_day_summary=pre_day_summary,
                                                                  current_user_question=current_user_question)

        elif current_state == KW_normal or current_time == KW_love:
            return get_result_from_prompt_sex(role_name=persona['name'],
                                              occupation=persona['occupation'],
                                              residence=persona['occupation'],
                                              hobbies=persona['occupation'],
                                              latest_history=latest_history,
                                              user_intention=user_intention,
                                              current_user_question=current_user_question)
        elif current_state == KW_telling:
            experience = None
            return get_result_from_prompt_telling(current_user_question=current_user_question, latest_history=latest_history, experience=experience)


        elif current_state == KW_sex:
            return get_result_from_prompt_sex(role_name=persona['name'],
                                              occupation=persona['occupation'],
                                              residence=persona['occupation'],
                                              hobbies=persona['occupation'],
                                              latest_history=latest_history,
                                              user_intention=user_intention,
                                              current_user_question=current_user_question)
        elif current_state == KW_whatsapp:
            return get_result_from_prompt_whatapp(current_user_question=current_user_question)
        elif current_state == KW_live:
            return get_result_from_prompt_from_live(role_name=persona['name'], latest_history=latest_history, current_user_question=current_user_question)
        elif current_state == KW_end:
            return get_result_from_prompt_end(role_name=persona['name'], current_user_question=current_user_question, latest_history=latest_history)
        elif current_state == KW_picture:
            return get_result_from_prompt_normal(role_name=persona['name'],
                                                 occupation=persona['occupation'],
                                                 residence=persona['occupation'],
                                                 hobbies=persona['occupation'],
                                                 latest_history=latest_history,
                                                 user_intention=user_intention,
                                                 current_user_question=current_user_question)
        return None
