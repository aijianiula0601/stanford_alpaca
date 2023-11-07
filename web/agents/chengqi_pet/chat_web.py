import gradio as gr
from aichat import PetChat
import config
import random
import time
import re

all_role_name_list = list(config.PERSONA_DICT.keys())

ai_chat = PetChat(all_role_name_list[-1])

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
    answer_text = ai_chat.question_response(chat_type, get_history_str(latest_history), \
        user_question, now_time, now_feed, now_emotion, now_work)

    role_robot = role_robot.split("(")[0]
    history[-1][-1] = f"{role_robot}: {answer_text}"

    return history, None


def chat_push_touch(now_time, now_feed, now_emotion, now_work, pet_push_history, touch_style, body_part,
           role_human: str = "user",
           role_robot: str = "robot",
           gpt_version: str = 'gpt3.5',
           ):
    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)
    chat_type = "touch"
    # ---------------------
    # 模型回复
    # ---------------------
    # res_text, now_time, now_feed, now_emotion, now_work, today_summary = \
    #     ai_chat.status_analysis(now_time, now_feed, now_emotion, today_work)
    touch_style_str = touch_style + body_part
    respond_text = \
        ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work, touch_type=touch_style_str)

    #历史推送一起打包
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
        emotion_text = mood_description(int(now_emotion.replace("'","")))
    except:
        pass

    return now_time, now_feed, now_emotion, emotion_text, now_work, pet_push_history

def chat_push_feed(now_time, now_feed, now_emotion, now_work, pet_push_history, feed_food,
           role_human: str = "user",
           role_robot: str = "robot",
           gpt_version: str = 'gpt3.5',
           ):
    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)
    chat_type = "feed"
    # ---------------------
    # 模型回复
    # ---------------------
    # res_text, now_time, now_feed, now_emotion, now_work, today_summary = \
    #     ai_chat.status_analysis(now_time, now_feed, now_emotion, today_work)

    respond_text = \
        ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work, food_type=feed_food)

    #历史推送一起打包
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
        emotion_text = mood_description(int(now_emotion.replace("'","")))
    except:
        pass
    return now_time, now_feed, now_emotion, emotion_text, now_work, pet_push_history

def chat_push_call(now_time, now_feed, now_emotion, today_work, pet_push_history, time_radio,
           role_human: str = "user",
           role_robot: str = "robot",
           gpt_version: str = 'gpt3.5',
           ):
    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)
    chat_type = "call_master"
    # ---------------------
    # 模型回复
    # ---------------------
    res_text, now_time, now_feed, now_emotion, now_work, today_summary = \
        ai_chat.status_analysis(now_time, now_feed, now_emotion, today_work, time_radio)

    respond_text = \
        ai_chat.question_response(chat_type, "", "", now_time, now_feed, now_emotion, now_work)

    #历史推送一起打包
    pet_push_history += respond_text + "\n"

    emotion_text = mood_description(79)
    try:
        emotion_text = mood_description(int(now_emotion.replace("'","")))
    except:
        pass

    return res_text, now_time, now_feed, now_emotion, emotion_text, now_work, today_summary, pet_push_history

def clear_f(role_human, role_robot):
    # 初始化机器人主动打招呼问候语
    history = [[]]
    ai_chat.update_state()

    return history, None, None, None, None


save_f = "chat_log.log"
open_save_f = open(save_f, 'a', buffering=1)


def save_chat_f(history: list, role_robot: str, gpt_version: str, comment_text: str):
    if len(history) > 0:
        open_save_f.write("-" * 100 + "\n")
        open_save_f.write("new chat\n")
        open_save_f.write(f"role_robot:{role_robot}\n")
        open_save_f.write(f"gpt:{gpt_version}\n")
        # open_save_f.write(f"comment_text:{comment_text}\n")
        open_save_f.write("-" * 100 + "\n")

        for qa in history:

            if qa[0] is not None:
                open_save_f.write(f"{qa[0]}\n")
            if qa[1] is not None:
                open_save_f.write(f"{qa[1]}\n")
            open_save_f.write("\n")

        gr.Info(f"save chat done, save file:{save_f}")

    else:
        gr.Warning("chat is empty!!!")


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# 文字版宠物聊天")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                limit_turn_n = gr.Slider(1, 10, step=1, value=5, label="保留的历史记录轮次", interactive=True)
                gpt_select = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Dropdown(value=all_role_name_list[-1], choices=all_role_name_list, label="角色选择",
                                         interactive=True)
                current_time = gr.Textbox(lines=1, value=time.strftime("%H:%M:%S", time.localtime()),
                                          label="now time", interactive=True)

            with gr.Row():
            #饱食度、心情、现在工作、今日总结
                feed_num = gr.Textbox(lines=1, value=100, label="饱食度", interactive=True)
                emotion_num = gr.Textbox(lines=1, value=100, visible=False, label="心情", interactive=True)
                emotion_text = gr.Textbox(lines=1, value="非常快乐", label="心情", interactive=True)
                work_status = gr.Textbox(lines=1, value="无聊中", label="现在在干嘛", interactive=True)

            pet_push = gr.Textbox(lines=3, value=None, label="宠物非文本互动消息", interactive=True)
            
            # with gr.Row():
            with gr.Row():
                time_radio = gr.Radio(["1h", "4h", "8h", "12h", "24h"], interactive=True, value="1h", label="时间拨动", info="模拟现实时间流动")
                with gr.Column():
                    touch_style = gr.Radio(["抚摸","挠痒","轻拍","拨弄"], label="抚摸方式", interactive=True, value="挠痒", info="怎么抚摸？")
                    petBodyPart = gr.Radio(["头部","背部","脚掌","腹部"], label="宠物部位", interactive=True, value="腹部", info="抚摸哪个部位？")
                food_radio = gr.Radio(["萝卜", "香蕉", "鱼", "草莓", "猕猴桃", "西瓜"], interactive=True, value="萝卜", label="食物种类", info="现在喂些什么？")
                
            
            with gr.Row():
                push_1h = gr.Button("时间向前")
                touch_human = gr.Button("模拟触摸宠物")
                feed_human = gr.Button("模拟投喂宠物")

            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

            # with gr.Row():



        # with gr.Column():
        #     with gr.Row():
        #         clear = gr.Button("clean history")
        #         save_chat = gr.Button("save to chat")

    today_summary = gr.Textbox(lines=3, value="在8点起床后，一直在无聊的等待主人", label="今天行为总结", interactive=True)
    debug_text = gr.Textbox(lines=3, value="", label="Debug内容", interactive=False)
    chatbot = gr.Chatbot()

            # chatbot = gr.Chatbot(label="history", value=[[]])

        #    history: list, user_question: str,
        #    chat_type, now_time, now_feed, now_emotion, now_work,
        #    role_human: str = "user",
        #    role_robot: str = "robot",
        #    limit_turn_n: int = 5,
        #    gpt_version: str = 'gpt3.5',
    user_input.submit(chat_f, [chatbot, user_input, 
        current_time, feed_num, emotion_num, work_status,
        role_human, role_robot, limit_turn_n, gpt_select],
        [chatbot, user_input],
        queue=False)

    push_1h.click(chat_push_call, [current_time, feed_num, emotion_num, today_summary, pet_push, time_radio,\
           role_human,role_robot,gpt_select], \
           [debug_text, current_time, feed_num, emotion_num, emotion_text, work_status, today_summary, pet_push], \
           queue=False)

    touch_human.click(chat_push_touch, [current_time, feed_num, emotion_num, work_status, pet_push, touch_style, petBodyPart, \
           role_human, role_robot, gpt_select], \
           [current_time, feed_num, emotion_num, emotion_text, work_status, pet_push], \
           queue=False)
    feed_human.click(chat_push_feed, [current_time, feed_num, emotion_num, work_status, pet_push, food_radio, \
           role_human, role_robot, gpt_select], \
           [current_time, feed_num, emotion_num, emotion_text, work_status, pet_push], \
           queue=False)
    
    # clear.click(clear_f, inputs=[role_human, role_robot],
    #             outputs=[chatbot, comment_text])
    # role_robot.change(clear_f, inputs=[role_human, role_robot],
    #                   outputs=[chatbot])

    # save_chat.click(save_chat_f, [chatbot, role_robot, gpt_select], None)

demo.queue().launch(server_name="0.0.0.0", server_port=8811)
