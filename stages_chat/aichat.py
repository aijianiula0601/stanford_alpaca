import json
import copy
import random

from utils import response_post_process, parse_key_value
from stages_chat.prompts.get_prompts import get_prompt_result, prompt_file_dic

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

    def __init__(self, role_data_dic: dict, gpt_version='gpt3.5'):
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
        self.role_name = role_data_dic['role_name']
        self.gpt_version = gpt_version
        # 历史聊天的总结
        self.previous_chat_summary = None
        self.role_picture_list = role_data_dic.get('pictures', [])
        # 如果用户问到要图片，转换到：直播间(live)、直接发图片(picture)
        self.ask_picture_change_to = "live"
        # 如果用户问到whatsapp等社交账号，转换到：直播间(live)、委婉拒绝
        self.ask_social_account_change_to = "live"

    def stages_chat(self, round_i: int, living_on: bool, latest_history_str: str, current_user_response: str, language: str = 'english'):
        """
        分阶段的聊天
        @param round_i: 轮次
        @param living_on: 是否在播
        @param latest_history_str: 聊天历史
        @param current_user_response: 当前用户的提问
        @param language: 采用什么语言回复
        @return: gpt的回复
        """

        # ---------------
        # 提前处理特殊情况
        # ---------------
        priority_process_reply = self._priority_process(anchor_virtual_id_living=living_on,
                                                        language=language,
                                                        current_user_response=current_user_response)
        if priority_process_reply:
            return None, priority_process_reply

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
        if round_i > 18:
            return self._stage4_chat(latest_history_str, current_user_response, language)

    def _priority_process(self, **kwargs):
        """
        优先处理模块
        @param kwargs:
            anchor_virtual_id_living: True or False
        @return:
        """

        # 如果主播分身处于直播状态
        if kwargs['anchor_virtual_id_living']:
            return self._branch_chat(branch_name='branch_anchor_virtual_id_live', **kwargs)

        else:
            return None

    def _live_stream_guide(self, **kwargs):
        """
        朋友引流(这个函数的引流方式可以修改，如修改为：大小号引流、主播分身引流)
        @param kwargs:
                latest_history_str: 最新的聊天历史，格式如下：
                    rosa: you busy?
                    user: no
                    rosa: Cool, what do you want to know?
                current_user_response: 当前用户的回复
                ...
        """
        return self._branch_chat(branch_name='branch_friend_live', **kwargs)

    def _branch_change(self, gpt_res: str, **kwargs):
        """
        分支转换控制
        Args:
             gpt_res: gpt的返回结果，格式为：
             {
                  "user_intention": "Curious about appearance",
                  "user_state": "Open to chatting",
                  "if_ask_social_software_account": false,
                  "if_ask_personal_picture": true,
                  "reply": "Why do you want to see my photo?"
             }
             kwargs:
                latest_history_str: 最新的聊天历史，格式如下：
                    rosa: you busy?
                    user: no
                    rosa: Cool, what do you want to know?
                current_user_response: 当前用户的回复
        """

        if_ask_social_software_account = parse_key_value(gpt_res, 'if_ask_social_software_account')
        if_ask_personal_picture = parse_key_value(gpt_res, 'if_ask_personal_picture')
        user_reply = parse_key_value(gpt_res, 'reply')

        # ------------------
        # 识别出要社交账号
        # ------------------
        if 'yes' in if_ask_social_software_account.lower() or 'true' in if_ask_social_software_account.lower():
            """
            可以切换到如下分支：
            1. 引导到直播间
            2. 委婉拒绝
            """
            # 1. 引导到直播间
            if self.ask_social_account_change_to == 'live':
                return self._live_stream_guide(language=kwargs['language'])
            # 2. 委婉拒绝
            else:
                return user_reply

        # ------------------
        # 识别出要照片
        # ------------------
        if 'yes' in if_ask_personal_picture.lower() or 'true' in if_ask_personal_picture.lower():
            """
            可以切换到如下分支：
            1. 发送照片
            2. 引导到直播间
                - 朋友身份引流
                - 大小号引流
                - 主播分身引流
            3. 委婉拒绝
            """

            # 1.发送照片
            if self.ask_picture_change_to == 'picture' and len(self.role_picture_list) > 0:
                pic_i = random.sample(range(0, len(self.role_picture_list)), k=1)[0]
                picture_dic = self.role_picture_list[pic_i]  # 获取照片dic
                del self.role_picture_list[pic_i]  # 删除已经发送的照片
                return self._branch_chat(branch_name='branch_picture',
                                         language=kwargs['language'],
                                         current_user_response=user_reply,
                                         photo_content=picture_dic["picture_content"])
            # 2.转到直播间
            elif self.ask_picture_change_to == 'live':
                return self._live_stream_guide(**kwargs)
            # 3.委婉拒绝
            else:
                return user_reply

        return user_reply

    def _branch_chat(self, branch_name, **kwargs):
        """
        进入各个分支的聊天
        Args:
            branch_name: 分支名字： sex, friend_live，...

            kwargs:
                latest_history_str: 最新的聊天历史，格式如下：
                    rosa: you busy?
                    user: no
                    rosa: Cool, what do you want to know?
                current_user_response: 当前用户的回复
                ...

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
        for k in kwargs:
            map_dic[k] = kwargs[k]

        role_answer = get_prompt_result(prompt_file=prompt_file_dic[branch_name],
                                        map_dic=map_dic,
                                        gpt_version=self.gpt_version)
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

        role_answer = get_prompt_result(prompt_file=prompt_file_dic['stage1_greeting'], map_dic=map_dic,
                                        gpt_version=self.gpt_version)
        return None, response_post_process(role_answer)

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

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage2_know_each_other'], map_dic=map_dic,
                                    gpt_version=self.gpt_version)

        return gpt_res, self._branch_change(gpt_res=gpt_res,
                                            latest_history=latest_history_str,
                                            current_user_response=current_user_response,
                                            language=language)

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

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage3_familiar'], map_dic=map_dic,
                                    gpt_version=self.gpt_version)
        return gpt_res, self._branch_change(gpt_res=gpt_res,
                                            latest_history=latest_history_str,
                                            current_user_response=current_user_response,
                                            language=language)

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

        gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage4_hot'], map_dic=map_dic,
                                    gpt_version=self.gpt_version)

        return gpt_res, self._branch_change(gpt_res=gpt_res,
                                            latest_history=latest_history_str,
                                            current_user_response=current_user_response,
                                            language=language)

    def summary_history(self, history_chat: str, previous_chat_history_summary_content: str):
        """
        @param history_chat: 聊天历史，字符串方式拼接起来
        @param previous_chat_history_summary_content: 之前已经总结的聊天历史内容
        @return: str
        """
        map_dic = {
            'history_chat': history_chat,
            'previous_chat_history_summary_content': previous_chat_history_summary_content,
        }
        res_text = get_prompt_result(prompt_file=prompt_file_dic['history_summary'],
                                     map_dic=map_dic,
                                     gpt_version=self.gpt_version)
        return res_text
