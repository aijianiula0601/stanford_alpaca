import gradio as gr
from aichat import PetChat, get_response
import config
import random
import time
import re

all_role_name_list = list(config.PERSONA_DICT.keys())

# 初始宠物
ai_chat = PetChat(all_role_name_list[0], gpt_version="gpt4")
# 朋友宠物
friend_ai_chat = PetChat(all_role_name_list[1], gpt_version="gpt4")


def init_two_pets():
    moli = PetChat(role_name="莫莉", gpt_version="4")
    bobo = PetChat(role_name="波波", gpt_version="4")

    moli.current = "莫莉正在看电视"
    bobo.current = "波波正在喝咖啡"

    moli.act_place = moli.decide_act_place(moli.current)
    bobo.act_place = bobo.decide_act_place(bobo.current)

    moli.focused_env = moli.get_focused_env(moli.act_place, moli.current)
    bobo.focused_env = bobo.get_focused_env(bobo.act_place, bobo.current)

    return moli, bobo


def mood_description(mood_value):
    if mood_value <= 20:
        return "极度沮丧"
    elif mood_value <= 40:
        return "不开心"
    elif mood_value <= 60:
        return "平静"
    elif mood_value <= 80:
        return "开心"
    else:
        return "非常快乐"


def get_history_str(history: list):
    if len(history) <= 0:
        return ''
    history_list = []
    for qa in history:
        for q_a in qa:
            if q_a is not None:
                history_list.append(q_a)
    return '\n'.join(history_list)


def get_latest_history(history: list, limit_turn_n: int):
    to_summary_history = []
    new_summary_flag = False
    if len(history) % limit_turn_n == 0 and len(history) // limit_turn_n > 1:
        if len(history) >= limit_turn_n * 2:
            new_summary_flag = True
            # 给过去做总结的历史
            to_summary_history = history[:-limit_turn_n][-limit_turn_n:]

    if new_summary_flag:
        latest_history = history[-limit_turn_n:]
    else:
        cur_turn_n = limit_turn_n + len(history) % limit_turn_n
        latest_history = history[-cur_turn_n:]

    return to_summary_history, latest_history


def chat_f(history,
           user_question,
           now_time, now_feed, now_emotion, now_work,
           role_human: str = "user",
           role_robot: str = "robot",
           limit_turn_n: int = 5,
           gpt_version: str = 'gpt3.5'):
    """
    主人跟宠物的聊天
    """
    history.append([f"{role_human}: {user_question}", None])

    chat_type = "chat_master"
    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)

    # ---------------------
    # 模型回复
    # ---------------------
    _, latest_history = get_latest_history(history[:-1], limit_turn_n)
    answer_text = ai_chat.question_response(chat_type, get_history_str(latest_history), user_question, now_time,
                                            now_feed, now_emotion, now_work)

    role_robot = role_robot.split("(")[0]
    history[-1][-1] = f"{role_robot}: {answer_text}"

    return history, None


def chat_push_touch(now_time, now_feed, now_emotion, now_work, pet_push_history, touch_style, body_part):
    """
    抚摸
    """
    # ---------------------
    # 重新设置环境
    # ---------------------
    chat_type = "touch"
    # ---------------------
    # 模型回复
    # ---------------------
    # res_text, now_time, now_feed, now_emotion, now_work, today_summary = \
    #     ai_chat.status_analysis(now_time, now_feed, now_emotion, today_work)
    touch_style_str = touch_style + body_part
    respond_text = \
        ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work,
                                  touch_type=touch_style_str)

    # 历史推送一起打包
    pet_push_history += respond_text + "\n"
    # emotion_text = mood_description(int(now_emotion.replace("'","")))

    satiety_pattern = r'饱食度：(.*?)，'
    # 提取心情的正则表达式
    mood_pattern = r'心情：(.*?)[】】]'
    satiety_match = re.search(satiety_pattern, respond_text)
    mood_match = re.search(mood_pattern, respond_text)
    if satiety_match:
        now_feed = satiety_match.group(1)
    if mood_match:
        now_emotion = mood_match.group(1)

    emotion_text = mood_description(79)
    try:
        emotion_text = mood_description(int(now_emotion.replace("'", "")))
    except:
        pass

    return now_time, now_feed, now_emotion, emotion_text, now_work, pet_push_history


def chat_push_feed(now_time, now_feed, now_emotion, now_work, pet_push_history, feed_food):
    """
    投喂
    """
    # ---------------------
    # 重新设置环境
    # ---------------------
    chat_type = "feed"

    # ---------------------
    # 模型回复
    # ---------------------
    respond_text = ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work,
                                             food_type=feed_food)

    # 历史推送一起打包
    pet_push_history += respond_text + "\n"

    satiety_pattern = r'饱食度：(.*?)，'
    # 提取心情的正则表达式
    mood_pattern = r'心情：(.*?)[】】]'
    satiety_match = re.search(satiety_pattern, respond_text)
    mood_match = re.search(mood_pattern, respond_text)
    if satiety_match:
        now_feed = satiety_match.group(1)
    if mood_match:
        now_emotion = mood_match.group(1)

    emotion_text = mood_description(79)
    try:
        emotion_text = mood_description(int(now_emotion.replace("'", "")))
    except:
        pass
    return now_time, now_feed, now_emotion, emotion_text, now_work, pet_push_history


def pets_chat(pet1, pet2, state1, state2, foc_mem1, foc_mem2, act_place):
    """
    规划一天的行程
    """
    prompt = config.chat_pets_prompt.format_map(
        {'pet1_info': pet1.pet_info(),
         'pet2_info': pet2.pet_info(),
         'pet1_state': state1,
         'pet2_state': state2,
         'pet1_foc_mem': foc_mem1,
         'pet2_foc_mem': foc_mem2,
         'act_place': act_place
         })
    """
    print("-" * 100)
    print(f"act place prompt:\n{prompt}")
    print("-" * 100)"""
    return get_response(prompt=prompt)


def time_forward_call(now_time, now_feed, now_emotion, today_work, pet_push_history, time_radio, work_status: str,
                      friend_work_status: str, public_screen: str):
    """
    时间拨动一个小时
    """
    # ---------------------
    # 重新设置环境
    # ---------------------

    chat_type = "call_master"
    # ---------------------
    # 模型回复
    # ---------------------
    res_text, now_time, now_feed, now_emotion, now_work, today_summary = \
        ai_chat.status_analysis(now_time, now_feed, now_emotion, today_work, time_radio)

    respond_text = \
        ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work)

    # 历史推送一起打包
    pet_push_history += respond_text + "\n"

    emotion_text = mood_description(79)
    try:
        emotion_text = mood_description(int(now_emotion.replace("'", "")))
    except:
        pass

    # -----------------------
    # 宠物自行行动，状态、事件
    # -----------------------
    act_place = ai_chat.decide_act_place(work_status)
    friend_act_place = friend_ai_chat.decide_act_place(friend_work_status)
    print("+++++++++++++++++++      活动位置    +++++++++++++++++++++++++++++++")
    print("莫莉活动位置:", act_place)
    print("波波活动位置:", friend_act_place)

    focused_env = ai_chat.get_focused_env(act_place, work_status)
    friend_focused_env = friend_ai_chat.get_focused_env(friend_act_place, friend_work_status)

    chat_deci_moli = ai_chat.decide_chat_plan(current_state=work_status, scenario=act_place,
                                              scenario_frind=friend_act_place,
                                              focused_mem=focused_env, pet_friend='波波',
                                              friend_current=friend_work_status)
    chat_deci_bobo = friend_ai_chat.decide_chat_plan(current_state=friend_work_status, scenario=friend_act_place,
                                                     scenario_frind=act_place,
                                                     focused_mem=friend_focused_env, pet_friend='莫莉',
                                                     friend_current=work_status)

    chat_content = None
    if '1' in chat_deci_moli and '1' in chat_deci_bobo:
        chat_content = pets_chat(pet1=ai_chat, pet2=friend_ai_chat, state1=work_status, state2=friend_work_status,
                                 foc_mem1=focused_env, foc_mem2=friend_focused_env, act_place=act_place)
        print('-' * 100)
        print("+++++++++++++++++++      开始聊天    +++++++++++++++++++++++++++++++")
        print(chat_content)
        summarized_chat = get_response(config.get_summarized_chat.format_map({'chat': chat_content}))
        ai_chat.memory_list.append(summarized_chat)
        friend_ai_chat.memory_list.append(summarized_chat)
        work_status = "刚刚莫莉和波波结束了一段对话，主要内容为：" + summarized_chat
        friend_work_status = "刚刚莫莉和波波结束了一段对话，主要内容为：" + summarized_chat

        if public_screen is None or public_screen == "":
            public_screen = f"[{now_time}] 【对话情况】{work_status} \n"
        else:
            public_screen = public_screen + f"[{now_time}] 【对话情况】{work_status}\n"

    else:
        plan_moli = ai_chat.act_plan(act_place=act_place, current_state=work_status, scenario_friend=friend_act_place,
                                     pet_friend="波波")
        plan_bobo = friend_ai_chat.act_plan(act_place=friend_act_place, current_state=friend_work_status,
                                            scenario_friend=friend_act_place, pet_friend="莫莉")
        print('-' * 100)
        print("+++++++++++++++++++      制定的计划    +++++++++++++++++++++++++++++++")
        print("莫莉的计划：", plan_moli)
        print("波波的计划：", plan_bobo)
        work_status = ai_chat.new_state(act_place=act_place, plan=plan_moli, pet_friend="波波", plan_friend=plan_bobo)
        friend_work_status = friend_ai_chat.new_state(act_place=friend_act_place, plan=plan_bobo, pet_friend="莫莉",
                                                      plan_friend=plan_moli)
        print("+++++++++++++++++++      当前的状态    +++++++++++++++++++++++++++++++")
        print(work_status)
        print(friend_work_status)
        ai_chat.memory_list.append(plan_moli)
        friend_ai_chat.memory_list.append(plan_bobo)

        if public_screen is None or public_screen == "":
            public_screen = f"[{now_time}] 【宠物】{work_status} 【朋友宠物】{friend_work_status}\n"
        else:
            public_screen = public_screen + f"[{now_time}] 【宠物】{work_status}【朋友宠物】{friend_work_status}\n"


    print("+++++++++++++++++++      决定的下一步动作    +++++++++++++++++++++++++++++++")
    print("莫莉决定的动作:", act_place)
    print("波波决定的动作:", friend_act_place)

    doing_now = ai_chat.doing_evn(work_status)
    friend_doing_now = friend_ai_chat.doing_evn(friend_work_status)

    print("+++++++++++++++++++      现在在做什么    +++++++++++++++++++++++++++++++")
    print(f"----宠物现在干什么:{doing_now}")
    print(f"----朋友宠物现在干什么:{friend_doing_now}")

    return res_text, now_time, now_feed, now_emotion, emotion_text, now_work, today_summary, pet_push_history, doing_now, friend_doing_now, focused_env, friend_focused_env, public_screen, chat_content


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# 文字版ai宠物聊天")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                limit_turn_n = gr.Slider(1, 10, step=1, value=20, label="保留的历史记录轮次", interactive=True,
                                         visible=False)
                gpt_select = gr.Dropdown(value='gpt4', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True, visible=False)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="主人名字", interactive=False, visible=False)
                role_robot = gr.Dropdown(value=all_role_name_list[0], choices=all_role_name_list, label="角色选择",
                                         interactive=False)
                current_time = gr.Textbox(lines=1, value=time.strftime("%H:%M:%S", time.localtime()),
                                          label="now time", interactive=True)

            with gr.Row():
                # 饱食度、心情、现在工作、今日总结
                feed_num = gr.Textbox(lines=1, value='100', label="饱食度", interactive=True)
                emotion_num = gr.Textbox(lines=1, value='100', visible=False, label="心情", interactive=True)
                emotion_text = gr.Textbox(lines=1, value="非常快乐", label="心情", interactive=True)

            with gr.Row():
                work_status = gr.Textbox(lines=1, value="莫莉正在看电视", label="宠物现在在干嘛", interactive=True)
                friend_work_status = gr.Textbox(lines=1, value="波波正在看电视", label="朋友宠物现在在干嘛",
                                                interactive=True)
                focused_env = gr.Textbox(lines=1, value=None, label="当前关注的事件", interactive=True, visible=False)
                friend_focused_env = gr.Textbox(lines=1, value=None, label="朋友当前关注的事件", interactive=True,
                                                visible=False)

            with gr.Row():
                pet_push = gr.Textbox(lines=3, max_lines=6, value=None, label="小组件推送", interactive=True)
                public_screen = gr.Textbox(lines=3, max_lines=6, value=None, label="公屏信息", interactive=True)

            with gr.Row():
                time_radio = gr.Radio(["1h", "4h", "8h", "12h", "24h"], interactive=True, value="1h", label="时间拨动",
                                      info="模拟现实时间流动")
                with gr.Column():
                    touch_style = gr.Radio(["抚摸", "挠痒", "轻拍", "拨弄"], label="抚摸方式", interactive=True,
                                           value="挠痒",
                                           info="怎么抚摸？")
                    petBodyPart = gr.Radio(["头部", "背部", "脚掌", "腹部"], label="宠物部位", interactive=True,
                                           value="腹部",
                                           info="抚摸哪个部位？")
                food_radio = gr.Radio(["萝卜", "香蕉", "鱼", "草莓", "猕猴桃", "西瓜"], interactive=True, value="萝卜",
                                      label="食物种类",
                                      info="现在喂些什么？")

            with gr.Row():
                push_1h = gr.Button("时间向前")
                touch_human = gr.Button("模拟触摸宠物")
                feed_human = gr.Button("模拟投喂宠物")

    today_summary = gr.Textbox(lines=3, value="在8点起床后，一直在无聊的等待主人", label="今天行为总结",
                               interactive=True, visible=False)
    debug_text = gr.Textbox(lines=3, value="", label="Debug内容", interactive=False, visible=False)

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")
            chatbot = gr.Chatbot()
        tow_pet_chat_tb = gr.Textbox(lines=1, value=None, label="两个宠物的对话内容", interactive=True)

    # 主人跟宠物的聊天
    user_input.submit(chat_f, [chatbot, user_input,
                               current_time, feed_num, emotion_num, work_status,
                               role_human, role_robot, limit_turn_n, gpt_select],
                      [chatbot, user_input],
                      queue=False)

    # 时间波动一个小时
    push_1h.click(time_forward_call,
                  [current_time, feed_num, emotion_num, today_summary, pet_push, time_radio, work_status,
                   friend_work_status, public_screen],
                  [debug_text, current_time, feed_num, emotion_num, emotion_text, work_status, today_summary, pet_push,
                   work_status, friend_work_status, focused_env, friend_focused_env, public_screen, tow_pet_chat_tb],
                  queue=False)

    # 抚摸
    touch_human.click(chat_push_touch,
                      [current_time, feed_num, emotion_num, work_status, pet_push, touch_style, petBodyPart],
                      [current_time, feed_num, emotion_num, emotion_text, work_status, pet_push], queue=False)
    # 投喂
    feed_human.click(chat_push_feed,
                     [current_time, feed_num, emotion_num, work_status, pet_push, food_radio],
                     [current_time, feed_num, emotion_num, emotion_text, work_status, pet_push],
                     queue=False)

demo.queue().launch(server_name="0.0.0.0", server_port=8991)
