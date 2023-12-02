import gradio as gr
from aichat import ChainOfThoughtChat
import config
import random
import time
import logging


log_path = '/mnt/cephfs2/changhengyi/llm/log/v4_bot/{}.log'.format(time.strftime("%Y_%m_%d_%H_%M"))
# logging.basicConfig(filename=log_path, format='%(message)s', level=logging.INFO)
logging.basicConfig(format='%(message)s', level=logging.INFO)


all_role_name_list = list(config.PERSONA_DICT.keys())

ai_chat = ChainOfThoughtChat(all_role_name_list[0])

initialize_greet_list = open('initialize_greet.txt', 'r').readlines()
second_day_greet_list = open('second_day_greet.txt', 'r').readlines()
logging.debug(f"---- initialize_greet_list len:{len(initialize_greet_list)} ----")
logging.debug(f"---- second_day_greet_list len:{len(second_day_greet_list)} ----")


def get_initialize_greet_text():
    return random.sample(initialize_greet_list, k=1)[0]


def get_second_day_greet_text():
    return random.sample(second_day_greet_list, k=1)[0]


def get_history_str(history: list):
    if len(history) <= 0:
        return ''
    history_list = []
    for qa in history:
        for q_a in qa:
            if q_a is not None and type(q_a) == str:
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


def chat_f(user_question: str,
           user_status: str,
           role_human: str = "user",
           role_robot: str = "robot",
           limit_turn_n: int = 5,
           gpt_version: str = 'gpt3.5',
           ):
    
    round_num = ai_chat.get_round()
    logging.info("█"*2+"[ ROUND: {} ]".format(round_num)+"█"*90)
    
    ai_chat.history.append([f"{role_human}: {user_question}", None])
    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)

    _, latest_history = get_latest_history(ai_chat.history[:-1], limit_turn_n)

    
    
    if round_num > 5 or ai_chat.state.end_greeting_flag == True:
        # ---------------------
        # 构建用户状态
        # ---------------------
        if user_status == "" or user_status is None:
            user_status = ai_chat.user_state()

        # ---------------------
        # 分析用户意图和聊天状态
        # ---------------------
        user_intention_state_text, user_intention, chat_state, chat_topic = ai_chat.intention_status_analysis(
            chat_history=get_history_str(latest_history),
            user_question=user_question,
            pic_topics=", ".join(ai_chat.pic_topics))
    else:
        user_status = ""
        user_intention_state_text, user_intention, chat_state, chat_topic = "", "", "", ""

    # ---------------------
    # 模型回复
    # ---------------------
    current_time = time.strftime("%H:%M:%S", time.localtime())
    answer_text, state_str = ai_chat.question_response(round_num=round_num,
                                            latest_history=get_history_str(latest_history),
                                            current_user_question=user_question,
                                            chat_state=chat_state,
                                            chat_topic=chat_topic,
                                            user_intention=user_intention,
                                            role_robot=role_robot,
                                            current_time=current_time)
    role_robot = role_robot.split("(")[0]
    ai_chat.history[-1][-1] = f"{role_robot}: {answer_text}"
    ai_chat.history_with_pic.append([f"{role_human}: {user_question}", f"{role_robot}: {answer_text}"])

    # ---------------------
    # 根据新的回复进行summary
    # ---------------------
    to_summary_history, _ = get_latest_history(ai_chat.history, limit_turn_n)

    if round_num % 5 == 0 and len(to_summary_history) > 0:
        history_summary = ai_chat.history_summary(chat_history=get_history_str(to_summary_history),
                                                  persona_name=role_robot)
    else:
        history_summary = ""
    
    ai_chat.chat_history_insert_pic()
    return ai_chat.history_with_pic, user_intention_state_text, None, history_summary, user_status, current_time, state_str


def clear_f(role_human, role_robot):
    # 初始化机器人主动打招呼问候语
    ai_chat.update_state(role_robot, get_initialize_greet_text())

    return ai_chat.history_with_pic, None, None, None, None


save_f = "chat_log.log"
open_save_f = open(save_f, 'a', buffering=1)


def another_day_f(role_robot):
    history_summary = ai_chat.history_summary_day(chat_history=get_history_str(ai_chat.history))
    # 初始化机器人主动打招呼问候语
    greeting_text = get_second_day_greet_text()
    ai_chat.update_day(history_summary, greeting_text)

    return ai_chat.history_with_pic, None, None, None, None


def save_chat_f(history: list, role_robot: str, gpt_version: str, comment_text: str):
    pass
    # if len(history) > 0:
    #     open_save_f.write("-" * 100 + "\n")
    #     open_save_f.write("new chat\n")
    #     open_save_f.write(f"role_robot:{role_robot}\n")
    #     open_save_f.write(f"gpt:{gpt_version}\n")
    #     open_save_f.write(f"comment_text:{comment_text}\n")
    #     open_save_f.write("-" * 100 + "\n")

    #     for qa in history:

    #         if qa[0] is not None:
    #             open_save_f.write(f"{qa[0]}\n")
    #         if qa[1] is not None:
    #             open_save_f.write(f"{qa[1]}\n")
    #         open_save_f.write("\n")

    #     gr.Info(f"save chat done, save file:{save_f}")

    # else:
    #     gr.Warning("chat is empty!!!")


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# State machine demo v4_bot 机器人接待")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                limit_turn_n = gr.Slider(1, 10, step=1, value=5, label="保留的历史记录轮次", interactive=True)
                gpt_select = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Dropdown(value=all_role_name_list[0], choices=all_role_name_list, label="角色选择",
                                         interactive=True)
                current_time = gr.Textbox(lines=1, value=time.strftime("%H:%M:%S", time.localtime()),
                                          label="now time", interactive=True)

            machine_state = gr.Textbox(lines=1, value=None, label="内在聊天状态信息", interactive=True)
            user_intention_state = gr.Textbox(lines=3, value=None, label="用户意图状态分析", interactive=False)
            user_status = gr.Textbox(lines=1, value=None, label="构建用户当前状态", interactive=True)
            history_summary = gr.Textbox(lines=3, value=None,
                                         label="聊天历史总结(只会在积累足够轮次后才开始做对话总结)", interactive=False)

        with gr.Column():
            with gr.Row():
                clear = gr.Button("clean history")
                another_day = gr.Button("Another day")
                save_chat = gr.Button("save to chat")

            greeting_text = get_initialize_greet_text()
            chatbot = gr.Chatbot(label="history", value=[[None, f"{role_robot.value.split('(')[0]}: {greeting_text}"]], height=700)
            ai_chat.init_greeting_text(greeting_text)
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")
            comment_text = gr.Textbox(value=None, label="评论", interactive=True)

    user_input.submit(chat_f, [user_input, user_status, role_human, role_robot, limit_turn_n, gpt_select],
                      [chatbot, user_intention_state, user_input, history_summary, user_status, current_time, machine_state],
                      queue=False)

    clear.click(clear_f, inputs=[role_human, role_robot],
                outputs=[chatbot, user_intention_state, history_summary, user_status, comment_text])
    role_robot.change(clear_f, inputs=[role_human, role_robot],
                      outputs=[chatbot, user_intention_state, history_summary, user_status, comment_text])

    save_chat.click(save_chat_f, [chatbot, role_robot, gpt_select, comment_text], None)
    another_day.click(another_day_f, inputs=[role_robot],
                outputs=[chatbot, user_intention_state, history_summary, user_status, comment_text])

demo.queue().launch(server_name="0.0.0.0", server_port=8881)
