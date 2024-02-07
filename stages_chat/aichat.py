import json
import copy

from utils import get_gpt_response, response_post_process, parse_key_value
from get_prompts import get_prompt_result, prompt_file_dic

# 人设信息json文件
role_json_file = "data/roles.json"


class PersonalInfo:
    def __init__(self, role_json_file):
        """
        人设信息
        """

        self.role_data_dic = json.load(open(role_json_file, 'r', encoding='utf-8'))

    def get_role_data(self, role_name):
        """
        根据人设名字获取人设信息
        Args:
            role_name: 人设名字

        Returns:
            一个dic，包含人设的信息，每个key保护特定信息，key有:
            name,
            occupation,
            residence,
            hobbies
        """
        return self.role_data_dic[role_name]


class AiChat:

    def __init__(self, role_data_dic, gpt_version='gpt3.5'):
        """
        初始化
        Args:
            role_data_dic: 人设信息的dic，格式如下：
                {
                    "name": "rosa",
                    "occupation": "Science and Technology Student",
                    "residence": "China",
                    "hobbies": "sports, traveling"
                }
            gpt_version: 采用的gpt版本，值：gpt4、gpt3.5
        """

        self.role_data_dic = role_data_dic
        self.gpt_version = gpt_version
        # 当前聊天阶段记录：stage1、stage2、stage3、stage4
        self.current_chat_stage = None
        # 历史聊天的总结
        self.previous_chat_summary = None

    def stages_chat(self, round_i: int, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        整个聊天的pipeline
        Args:
            round_i: 目前是第几轮的聊天
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:

        """

        # ---------------
        # stage1
        # ---------------
        if round_i <= 5:
            return self._stage1_chat(latest_history_str, current_user_response, language)

        # ---------------
        # stage2
        # ---------------
        if 5 < round_i < 12:
            return self._stage2_chat(latest_history_str, current_user_response, language)

        # ---------------
        # stage3
        # ---------------
        if 12 < round_i < 18:
            return self._stage3_chat(latest_history_str, current_user_response, language)

        # ---------------
        # stage4
        # ---------------
        if 18 < round_i < 20:
            return self._stage4_chat(latest_history_str, current_user_response, language)

    def _branch_chat(self, branch_name, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        进入各个分支的聊天
        Args:
            branch_name: 分支名字： sex, friend_live，...
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:
            返回json实例，分析用户意图，状态等信息，回复格式如下：
            {
              "user_intention": "Curious about appearance",
              "user_state": "Open to chatting",
              "if_ask_social_software_account": false,
              "if_ask_personal_picture": true,
              "reply": "Why do you want to see my photo?"
            }
        """

        map_dic = copy.deepcopy(self.role_data_dic)
        map_dic['latest_history'] = latest_history_str
        map_dic['current_user_response'] = current_user_response
        map_dic['previous_chat_summary'] = self.previous_chat_summary
        map_dic['language'] = language

        role_answer = get_prompt_result(prompt_file=prompt_file_dic[branch_name], map_dic=map_dic, gpt_version=self.gpt_version)
        return response_post_process(role_answer)

    def _stage1_chat(self, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        阶段1聊天，聊天轮次小于5
        Args:
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:
            gpt生成的回复，人设回复用户的话语
        """

        map_dic = copy.deepcopy(self.role_data_dic)
        map_dic['latest_history'] = latest_history_str
        map_dic['current_user_response'] = current_user_response
        map_dic['language'] = language

        role_answer = get_prompt_result(prompt_file=prompt_file_dic['stage1_greeting'], map_dic=map_dic, gpt_version=self.gpt_version)
        return response_post_process(role_answer)

    def _stage2_chat(self, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        阶段2聊天，5 < 聊天轮次 < 10
        Args:
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:
            返回json实例，分析用户意图，状态等信息，回复格式如下：
            {
              "user_intention": "Curious about appearance",
              "user_state": "Open to chatting",
              "if_ask_social_software_account": false,
              "if_ask_personal_picture": true,
              "reply": "Why do you want to see my photo?"
            }
        """
        map_dic = copy.deepcopy(self.role_data_dic)
        map_dic['latest_history'] = latest_history_str
        map_dic['current_user_response'] = current_user_response
        map_dic['language'] = language

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage2_know_each_other'], map_dic=map_dic, gpt_version=self.gpt_version)
        if_ask_social_software_account = parse_key_value(gpt_res, 'if_ask_social_software_account')
        if_ask_personal_picture = parse_key_value(gpt_res, 'if_ask_personal_picture')
        reply = parse_key_value(gpt_res, 'reply')

        return if_ask_social_software_account, if_ask_personal_picture, reply

    def _stage3_chat(self, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        阶段2聊天，10 < 轮次 < 15
        Args:
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:
            返回json实例，分析用户意图，状态等信息，回复格式如下：
            {
              "user_intention": "Curious about appearance",
              "user_state": "Open to chatting",
              "if_ask_social_software_account": false,
              "if_ask_personal_picture": true,
              "reply": "Why do you want to see my photo?"
            }
        """
        map_dic = copy.deepcopy(self.role_data_dic)
        map_dic['latest_history'] = latest_history_str
        map_dic['current_user_response'] = current_user_response
        map_dic['previous_chat_summary'] = self.previous_chat_summary
        map_dic['language'] = language

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage3_familiar'], map_dic=map_dic, gpt_version=self.gpt_version)
        if_ask_social_software_account = parse_key_value(gpt_res, 'if_ask_social_software_account')
        if_ask_personal_picture = parse_key_value(gpt_res, 'if_ask_personal_picture')
        reply = parse_key_value(gpt_res, 'reply')

        return if_ask_social_software_account, if_ask_personal_picture, reply

    def _stage4_chat(self, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        阶段2聊天，15 < 轮次
        Args:
            latest_history_str: 最新的聊天历史，格式如下：
                rosa: you busy?
                user: no
                rosa: Cool, what do you want to know?
            current_user_response: 当前用户的回复
            language: 采用什么语言回复

        Returns:
            返回json实例，分析用户意图，状态等信息，回复格式如下：
            {
              "user_intention": "Curious about appearance",
              "user_state": "Open to chatting",
              "if_ask_social_software_account": false,
              "if_ask_personal_picture": true,
              "reply": "Why do you want to see my photo?"
            }
        """
        map_dic = copy.deepcopy(self.role_data_dic)
        map_dic['latest_history'] = latest_history_str
        map_dic['current_user_response'] = current_user_response
        map_dic['previous_chat_summary'] = self.previous_chat_summary
        map_dic['language'] = language

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage4_hot'], map_dic=map_dic, gpt_version=self.gpt_version)
        if_ask_social_software_account = parse_key_value(gpt_res, 'if_ask_social_software_account')
        if_ask_personal_picture = parse_key_value(gpt_res, 'if_ask_personal_picture')
        reply = parse_key_value(gpt_res, 'reply')

        return if_ask_social_software_account, if_ask_personal_picture, reply
