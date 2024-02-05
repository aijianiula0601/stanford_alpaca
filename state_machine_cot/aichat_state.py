import json
import random
import logging
import time

from prompt import state_cot_config

from tools import (
    parse_result_of_analysis_chat
, edit_distance_of_sentence
, get_history_str
, get_gpt35_response
, get_gpt4_response
)


class AIChat:
    def __init__(self, role_name="Aysha", gpt_version: str = '3.5'):
        """
        受线上redis缓存的方式的限制，无法为每个用户分别维护一个AIChat对象的实例，所以内在状态等变量没有写成该类的成员变量。
        本质上还是偏面向过程的方式去实现。
        下面定义的三个变量都是固定不动的，分别是问候的轮次、结束的轮次、还有用来暂时存放一些变量的key_info字典。
        """
        self.gpt_version = '3.5'
        self.greeting_rounds = 3
        self.end_rounds = 20
        self.key_info = {}
        self.pic_list = ['pictures/rosa/1.jpg', 'pictures/rosa/2.jpg', 'pictures/rosa/3.jpg', 'pictures/rosa/4.jpg']

    def analysis_state(self, round_num, chat_state, current_user_question, user_intention, willingness_score, story_topic, story_topics, old_state_history):
        """
        功能：依靠传入的这些参数，判断最终的状态。
        参数解释：
            round_num: 聊天轮次
            chat_state: gpt判断出来的状态( normal, picture, whatsapp, sex, real, telling 中的一个)
            current_user_question: 用户最新说的话
            willingness_score: 判断出来的用户聊天意愿，取值在{1, 2}
            story_topic: gpt判断出来的聊天话题, 例如friends movies
            story_topics: 当前话题的列表, 讲过的话题会remove, 解锁了新话题会append进来
            old_state_history: 之前的状态历史列表, 例如['greeting', 'greeting', 'greeting', 'telling:friends', 'live', 'picture', 'sex', 'sex']
        """
        logging.info("round_num={} chat_state={} current_user_question={} story_topic={} old_state_history={}".format(
            round_num, chat_state, current_user_question, story_topic, json.dumps(old_state_history)
        ))
        # 第一个状态使用greeting
        if len(old_state_history) == 0:
            current_state = 'greeting'

        # end状态的条件是，轮次大于终止轮次，且用户聊天意愿不积极时
        elif round_num > self.end_rounds and willingness_score == 1:
            current_state = 'end'

        # picture状态：gpt判断是picture状态，而且前一个状态不是picture状态，也就是picture状态不能连续两次。
        elif chat_state == 'picture' and old_state_history[-1] != 'picture':
            current_state = 'picture'

        # "whatsapp" 状态
        elif chat_state == "whatsapp" and old_state_history[-1] != 'whatsapp':
            current_state = chat_state

        # story_topic为bigolive时推荐直播，
        # 推荐完删掉bigolive这个topic，确保不会重复推荐。
        elif story_topic == 'bigolive' or ('bigolive' in story_topics and round_num >= 10):
            current_state = 'live'
            story_topics.remove('bigolive')

        # 如果要了照片或者whatsapp账号，用直播引流状态去承接
        elif old_state_history[-1] == 'whatsapp':
            if 'bigolive' in story_topics:
                current_state = 'live'
                story_topics.remove('bigolive')
            else:
                current_state = 'normal'

        # picture状态后一定是normal状态
        elif old_state_history[-1] == 'picture':
            current_state = 'normal'

        # 依据关键词匹配的方式不稳定，暂时不用
        # elif keywords_matching(['picture', 'pictures', 'photo', 'photos'], user_intention):
        #     current_state = 'picture'

        # 一旦出现sex状态，持续5次，之后转为normal状态
        elif old_state_history[-1] == 'sex':
            if old_state_history[-5:].count('sex') == 5:
                current_state = 'normal'
            else:
                current_state = 'sex'

        # 一旦出现telling状态，持续1次，之后转为normal状态
        elif old_state_history[-1].startswith('telling'):
            current_state = 'normal'

        # 一旦出现real状态，持续两次，之后转为normal状态
        elif old_state_history[-1] == 'real':
            current_state = 'normal'

        # 前几轮如果没有其他状态插入，就一直是greeting状态
        elif round_num <= self.greeting_rounds and old_state_history[-1] == 'greeting':
            current_state = "greeting"

        # 进入telling状态的条件是：
        # 1. 前两次不是telling状态（不希望频繁发起新话题）
        # 2. 状态判断为telling状态且有候选话题可讲
        elif len(old_state_history) >= 2 and not old_state_history[-1].startswith('telling') and not old_state_history[-2].startswith('telling') and \
                (chat_state == "telling" and len(story_topics)):
            if story_topic in story_topics:
                topic = story_topic
            else:
                topic = random.choice(story_topics)
            current_state = "telling:" + topic
            story_topics.remove(topic)  # 这变量是引用，所以会删除原列表中的元素

        # 其余情况交给cot模块，调用gpt去判断
        elif chat_state in ["normal", "sex"]:
            current_state = chat_state

        # 如果判断不了，就是normal状态
        else:
            current_state = "normal"

        old_state_history.append(current_state)
        self.key_info['current_steate'] = current_state
        logging.info("analysis state uidpair={} current_state={}".format(self.uid_pair, current_state))
        return old_state_history

    def get_prompt(self,
                   persona: dict,
                   latest_history: str,
                   current_user_question: str,
                   user_intention: str,
                   current_time: str,
                   language: str,
                   chat_day: int,
                   state_history: list,
                   pre_day_summary: str):
        """
        功能: 根据状态获取prompt
        参数解释：
            persona: 人物个人资料的字典，包含name、occupation等
            latest_history: 最近几轮的聊天历史，默认为5轮 
            current_user_question: 用户当前最新的一句回复
            user_intention: 用户意图，由上一步gpt判断出来的
            current_time: 当前时间 
            language: 语言，用于指定gpt用何种语言回复
            chat_day: 聊天的天数，暂时不用
            state_history: 之前的状态历史列表, 例如['greeting', 'greeting', 'greeting', 'telling:friends', 'live', 'picture', 'sex', 'sex']
            pre_day_summary: 前一天聊天内容的总结
        """
        cal_state = state_history[-1].split(":")[0]
        story = ""
        if len(state_history) and state_history[-1].startswith('telling') and state_history[-1].split(':')[1] in self.story_data:
            story = self.story_data[state_history[-1].split(':')[1]][1]
        greeting_task = 'explain that you want to be friends with him, ask him where he comes from. Do it step by step.'
        format_map_dic = {
            'language': language,
            'name': persona['name'],
            'occupation': persona['occupation'],
            'residence': persona['residence'],
            'hobbies': persona['hobbies'],
            'latest_history': latest_history,
            'current_user_question': current_user_question,
            'user_intention': user_intention,
            'current_time': current_time,
            'task': greeting_task,
            'story': story.format_map({'name': persona['name']}),
        }

        prompt = state_cot_config[self.exp_tag]["STATE_PROMPT_DICT"][cal_state].format_map(format_map_dic)
        self.key_info['state_for_prompt'] = cal_state
        return prompt

    def question_response(self, round_num: int,
                          latest_history: str,
                          current_user_question: str,
                          chat_state: str,
                          willingness_score: int,
                          story_topic: str,
                          user_intention: str,
                          role_robot: str,
                          current_time: str,
                          user_language_code: str,
                          day: int,
                          pre_day_summary: str,
                          state_history: list):
        """
        功能: 获取回复，包含三步
            1. analysis_state 判断状态
            2. get_prompt 组装prompt
            3. chat_with_chatgpt_v2 调用gpt
            4. 对生成的回复做后处理
        参数解释：
            round_num: 聊天轮次
            latest_history: 最近几轮的聊天历史，默认为5轮 
            current_user_question: 用户当前最新的一句回复 
            chat_state: 聊天状态（由聊天分析模块获取）
            willingness_score: 聊天意愿得分（由聊天分析模块获取）
            story_topic: 第聊天主题（由聊天分析模块获取）
            user_intention: 用户意图（由聊天分析模块获取）
            role_robot: 聊天机器人的角色名字
            current_time: 当前时间
            user_language_code: 规定机器人使用的语言
            day: 第几天聊天
            pre_day_summary: 前一天聊天的总结
            state_history: 之前的状态历史列表, 例如['greeting', 'greeting', 'greeting', 'telling:friends', 'live', 'picture', 'sex', 'sex']
        """
        # [1]: 分析状态
        new_state_history = self.analysis_state(round_num, chat_state,
                                                current_user_question, user_intention,
                                                willingness_score, story_topic,
                                                self.story_topics, state_history)

        # [2]: 生成回复
        logging.info("=" * 100)
        logging.info('【2】：生成回复 ({})'.format(new_state_history[-1]))
        logging.info("=" * 100)

        if new_state_history[-1] == 'picture' and len(self.pic_list):
            res = 'Here is my selfie. [send a picture of her self]'
            finish_reason = ''

            return res, finish_reason, new_state_history

        prompt = self.get_prompt(self.persona,
                                 latest_history,
                                 current_user_question,
                                 user_intention,
                                 current_time,
                                 user_language_code,
                                 day,
                                 new_state_history,
                                 pre_day_summary)

        # 根据prompt请求gpt生成回复，如果回复中有自爆穿帮的情况，就重新请求一次，最多请求5次
        # message_list = [{"role": 'user', 'content': prompt}, {"role": 'user', 'content': current_user_question}]
        message_list = [{"role": 'user', 'content': prompt}]
        logging.info(f'{prompt}')
        logging.info("-" * 100)

        if self.gpt_version == '3.5':
            res, finish_reason, total_tokens = get_gpt35_response(message_list), "", 0
        else:
            res, finish_reason, total_tokens = get_gpt4_response(message_list), "", 0

        logging.info("-" * 100)
        logging.info(f"{res}")
        logging.info("-" * 100)

        # 简单的后处理，去掉之前的说话人，或去掉后面的label
        role_robot = role_robot.split("(")[0]
        res = res.strip().split('\n')[-1].strip('"')
        res = res if not res.lower().startswith(f"{role_robot.lower()}:") else res[len(f"{role_robot}:"):]
        res = res.rstrip(':)').rstrip(';)').split('#')[0]
        res = res.split('(')[0].split('（')[0]

        return res, finish_reason, new_state_history

    def post_processing(self, history, history_with_pic, willingness_score, old_intimacy_score):
        selected_pic = ''  # 暂时去掉发送照片功能
        # [1]: 选择照片并发送
        last_response = history_with_pic[-1][1]
        if edit_distance_of_sentence(last_response, 'Here is my selfie') <= 1:
            selected_pic = random.choice(self.pic_list)
            history_with_pic[-1][1] = [selected_pic]
            self.pic_list.remove(selected_pic)

        # --------------------------
        # [2]: 统计亲密度得分
        # 解锁更多剧情故事
        # --------------------------
        # self.intimacy_score += willingness_score
        new_intimacy_score = old_intimacy_score + willingness_score
        logging.info("del in pic_dict uidpair={} old_intimacy_score={} will_score={}".format(self.uid_pair, old_intimacy_score, willingness_score))
        for topic in self.story_data:
            score_th = self.story_data[topic][0]
            if new_intimacy_score >= score_th > new_intimacy_score - willingness_score:
                self.story_topics.append(topic)
        return new_intimacy_score, self.story_topics, history, history_with_pic, selected_pic

    def chat_analysis(self, chat_history: str, user_question: str, last_state_history: list):
        """
        功能: 
            对话分析模块，调用一次gpt，分析对话，得到的一些结果用于决定最终的状态
        参数解释：
            chat_history: 聊天历史
            user_question: 用户当前的回复
        返回的参数：
            str_res: 格式化显示一下结果，方便看日志
            short_summary: gpt对最近几轮聊天的总结，暂时没有用到
            user_intention: gpt分析出的用户意图
            chat_state: gpt分析出的状态（不一定是最终的状态，最终状态还要考虑别的变量综合判断）
            story_topic: gpt分析出来的
            willingness_score:
        """
        format_map_dic = {
            'chat_history': chat_history,
            'user_question': user_question,
            'story_topics': ', '.join(self.story_topics),
        }
        if len(last_state_history) == 0 or (len(last_state_history) < 3 and last_state_history[-1] == 'greeting'):
            prompt = state_cot_config[self.exp_tag]["PROMPT_DIC"]['chat_analysis_simple'].format_map(format_map_dic)
        else:
            prompt = state_cot_config[self.exp_tag]["PROMPT_DIC"]['chat_analysis'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        if self.gpt_version == '3.5':
            res_text, finish_reason, total_tokens = get_gpt35_response(message_list), "", 0
        else:
            res_text, finish_reason, total_tokens = get_gpt4_response(message_list), "", 0

        short_summary, user_intention, chat_state, story_topic, willingness_score = parse_result_of_analysis_chat(res_text)

        str_res = (
            "short_summary: {}\n"
            "user_intention: {}\n"
            "chat_state: {}\n"
            "story_topic: {}\n"
            "willingness_score: {}\n"
        ).format(short_summary, user_intention, chat_state, story_topic, willingness_score)
        print(str_res)
        logging.info("=" * 100)
        logging.info('【1】：状态分析')
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(res_text)
        logging.info("-" * 100)
        logging.info("uidpair={} chat_analysis_res={} willingness_score={}".format(self.uid_pair, json.dumps(str_res), willingness_score))
        return str_res, short_summary, user_intention, chat_state, story_topic, willingness_score

    def history_summary_day(self, chat_history: str):
        """
        一整天的历史信息总结
        """

        format_map_dic = {
            "chat_history": chat_history,
        }

        prompt = state_cot_config[self.exp_tag]["PROMPT_DIC"]['history_summary_day'].format_map(format_map_dic)
        message_list = [{"role": "user", "content": prompt}]
        # res_text = get_gpt_result(self.engine_name, message_list)
        if self.gpt_version == '3.5':
            res_text, finish_reason, total_tokens = get_gpt35_response(message_list), "", 0
        else:
            res_text, finish_reason, total_tokens = get_gpt4_response(message_list), "", 0

        logging.info("=" * 100)
        logging.info('【0】：history_summary_day')
        logging.info("=" * 100)
        logging.info(f'{prompt}')
        logging.info("-" * 100)
        logging.info(f"{res_text}")
        logging.info("-" * 100)
        logging.info("uidpair={} summary_day={}".format(self.uid_pair, res_text))

        return res_text

    def chat_main(self,
                  round_num: int,
                  history: list,
                  history_with_pic: list,
                  user_question: str,
                  openai_config: list,
                  robot_role_attr: dict,
                  cur_time: str,
                  exp_tag: str,
                  robot_uid: str,
                  user_uid: str,
                  user_language_code: str,
                  day: int,
                  old_intimacy_score: int,
                  story_topics: list,
                  story_data,
                  last_state_history,
                  send_pic_flag: bool = False,
                  split_respose_flag: bool = False,
                  role_human: str = "user",
                  role_robot: str = "robot",
                  limit_turn_n: int = 4,
                  gpt_version: str = 'gpt35',
                  ):

        self.uid_pair = "{} {}".format(robot_uid, user_uid)
        self.openai_config = openai_config
        persona_key = 'robot_{}'.format(gpt_version)
        self.robot_role_attr = robot_role_attr
        self.tokens_monitor = dict()

        self.exp_tag = exp_tag
        self.key_info = dict()

        self.role_name = role_robot
        self.send_pic_flag = send_pic_flag
        self.split_response_flag = split_respose_flag
        self.intimacy_score = 5
        self.story_topics = story_topics
        self.story_data = story_data

        self.prompt_dict = state_cot_config[self.exp_tag]['PROMPT_DIC']
        self.persona = state_cot_config[self.exp_tag]['PERSONA_DICT'][self.role_name]

        self.key_info['last_intimacy_score'] = old_intimacy_score
        self.key_info['old_state_history'] = last_state_history
        self.key_info['old_story_topics'] = story_topics
        self.key_info['old_story_data'] = story_data
        self.key_info['old_history'] = history
        self.key_info['old_history_with_pic'] = history_with_pic

        history.append([f"{role_human}: {user_question}", None])

        # -------------------------------------------------------------------------------------------------------------------
        # 【1】：第一次调用gpt，首先调用chat_analysis，分析聊天，得到user_intention, chat_state, story_topic, willingness_score
        # _, latest_history = get_latest_history(history[:-1], limit_turn_n)
        latest_history = history[-limit_turn_n - 1:-1]
        # if round_num > self.greeting_rounds or (len(last_state_history) and last_state_history[-1] != 'greeting'):
        str_res, short_summary, user_intention, chat_state, story_topic, willingness_score = self.chat_analysis(
            chat_history=get_history_str(latest_history),
            user_question=user_question,
            last_state_history=last_state_history
        )

        # 如果第二天重新开始聊天，对前一天的内容做个总结，该功能暂时没有用到
        pre_day_summary = ""
        # if day > 1:
        #     _, latest_k_history = get_latest_history(history=history, limit_turn_n=20)
        #     pre_day_summary = self.history_summary_day(chat_history=get_history_str(latest_k_history))
        #     print("*"*10)
        #     print("pre_day_summary: {}".format(pre_day_summary))
        #     print("*"*10)
        # else:
        #     pre_day_summary = ""

        # 【2】：第二次调用gpt，生成回复
        current_time = time.strftime("%H:%M:%S", time.localtime())
        answer_text, finish_reason, new_state_history = self.question_response(round_num=round_num,
                                                                               latest_history=get_history_str(latest_history),
                                                                               current_user_question=user_question,
                                                                               chat_state=chat_state,
                                                                               willingness_score=willingness_score,
                                                                               story_topic=story_topic,
                                                                               user_intention=user_intention,
                                                                               role_robot=role_robot,
                                                                               current_time=current_time,
                                                                               user_language_code=user_language_code,
                                                                               day=day,
                                                                               pre_day_summary=pre_day_summary,
                                                                               state_history=last_state_history)
        # 将得到的最新的回复加入到历史列表里面
        # 这里有两个聊天历史列表history和history_with_pic其实在实际线上只会用到history，
        # history_with_pic只用于测试的时候方便显示照片。
        role_robot = role_robot.split("(")[0]
        history[-1][-1] = f"{role_robot}: {answer_text}"
        history_with_pic.append([f"{role_human}:{user_question}", f"{role_robot}: {answer_text}"])

        # 【3】后处理，添加图片，规范一下格式等功能
        new_intimacy_score, new_story_topics, new_history, new_history_with_pic, selected_pic \
            = self.post_processing(history, history_with_pic, willingness_score, old_intimacy_score)
        # -------------------------------------------------------------------------------------------------------------------

        self.key_info['new_intimacy_score'] = new_intimacy_score
        self.key_info['new_story_topics'] = new_story_topics
        self.key_info['new_history'] = new_history
        self.key_info['new_history_with_pic'] = new_history_with_pic
        self.key_info['selected_pic'] = selected_pic
        self.key_info['new_state_history'] = new_state_history

        return answer_text, \
               finish_reason, \
               self.tokens_monitor, \
               new_history, \
               new_history_with_pic, \
               new_intimacy_score, \
               new_state_history, \
               new_story_topics, \
               selected_pic, \
               self.key_info
