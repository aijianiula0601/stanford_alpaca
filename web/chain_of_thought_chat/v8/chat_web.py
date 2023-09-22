import gradio as gr
from aichat import ChainOfThoughtChat
import config
import random
import time

all_role_name_list = list(config.PERSONA_DICT.keys())

ai_chat = ChainOfThoughtChat(all_role_name_list[-1])

initialize_greet_list = open('initialize_greet.txt', 'r').readlines()
print(f"---- initialize_greet_list len:{len(initialize_greet_list)} ----")


def get_initialize_greet_text(role_human, role_robot):
    return random.sample(initialize_greet_list, k=1)[0].format_map(
        {"YourName": role_robot.split('(')[0], "UserName": role_human})


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


def chat_f(history: list,
           user_question: str,
           user_status: str,
           last_summary: str,
           role_human: str = "user",
           role_robot: str = "robot",
           limit_turn_n: int = 5,
           gpt_version: str = 'gpt3.5',
           ):
    history.append([f"{role_human}: {user_question}", None])

    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)

    # ---------------------
    # 构建状态
    # ---------------------
    if user_status == "" or user_status is None:
        user_status = ai_chat.user_state()

    # ---------------------
    # 分析用户意图和状态
    # ---------------------
    _, latest_history = get_latest_history(history[:-1], limit_turn_n)

    user_intention_state_text, user_intention, user_state = ai_chat.intention_status_analysis(
        chat_history=get_history_str(latest_history),
        user_question=user_question)

    # ---------------------
    # 模型回复
    # ---------------------
    current_time = time.strftime("%H:%M:%S", time.localtime())
    answer_text = ai_chat.question_response(last_summary=last_summary,
                                            latest_history=get_history_str(latest_history),
                                            current_user_question=user_question,
                                            user_state=user_state,
                                            user_intention=user_intention,
                                            role_robot=role_robot,
                                            current_time=current_time)
    role_robot = role_robot.split("(")[0]
    history[-1][-1] = f"{role_robot}: {answer_text}"

    # ---------------------
    # 根据新的回复进行summary
    # ---------------------
    to_summary_history, _ = get_latest_history(history, limit_turn_n)

    if len(to_summary_history) <= 0:
        history_summary = last_summary
    else:
        history_summary = ai_chat.history_summary(chat_history=get_history_str(to_summary_history),
                                                  last_summary=last_summary,
                                                  persona_name=role_robot)
    print("\n" * 5)
    print("+" * 200)
    print("new chat")
    print("+" * 200)
    return history, user_intention_state_text, None, history_summary, user_status, current_time


def clear_f(role_human, role_robot):
    # 初始化机器人主动打招呼问候语
    history = [[None, f"{role_robot.split('(')[0]}: {get_initialize_greet_text(role_human, role_robot)}"]]

    return history, None, None, None


save_f = "chat_log.log"

open_save_f = open(save_f, 'a', buffering=1)


def save_chat_f(history: list):
    if len(history) > 0:
        open_save_f.write("-" * 100 + "\n")
        open_save_f.write("new chat\n")
        open_save_f.write("-" * 100 + "\n")

        for qa in history:

            if qa[0] is not None:
                open_save_f.write(f"{qa[0]}\n")
            if qa[1] is not None:
                open_save_f.write(f"{qa[1]}\n")
            open_save_f.write("\n")

        gr.Info("save chat done!")

    else:
        gr.Warning("chat is empty!!!")


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# chain-of-thought 聊天demo")
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

            user_intention_state = gr.Textbox(lines=3, value=None, label="用户意图状态分析", interactive=False)
            user_status = gr.Textbox(lines=1, value=None, label="构建用户当前状态", interactive=True)
            history_summary = gr.Textbox(lines=3, value=None,
                                         label="聊天历史总结(只会在积累足够轮次后才开始做对话总结)", interactive=False)

        with gr.Column():
            with gr.Row():
                clear = gr.Button("clean history")
                save_chat = gr.Button("save to chat")
            chatbot = gr.Chatbot(label="history", value=[
                [None, f"{role_robot.value.split('(')[0]}: {get_initialize_greet_text(role_human, role_robot.value)}"]])
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input.submit(chat_f, [chatbot, user_input, user_status, history_summary, role_human, role_robot,
                               limit_turn_n, gpt_select],
                      [chatbot, user_intention_state, user_input, history_summary, user_status, current_time],
                      queue=False)

    clear.click(clear_f, inputs=[role_human, role_robot],
                outputs=[chatbot, user_intention_state, history_summary, user_status])
    role_robot.change(clear_f, inputs=[role_human, role_robot],
                      outputs=[chatbot, user_intention_state, history_summary, user_status])

    save_chat.click(save_chat_f, chatbot, None)

demo.queue().launch(server_name="0.0.0.0", server_port=8808)
