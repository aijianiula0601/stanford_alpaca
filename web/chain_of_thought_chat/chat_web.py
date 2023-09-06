import gradio as gr
from aichat import ChainOfThoughtChat

ai_chat = ChainOfThoughtChat()


def get_limit_history(history: list[list], limit_turn_n=0):
    history_list = []
    for qa in history[-limit_turn_n:]:
        for q_a in qa:
            if q_a is not None:
                history_list.append(q_a)

    return '\n'.join(history_list)


def chat_f(history: list,
           user_question: str,
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
    # 分析用户意图和状态
    # ---------------------
    limit_history = get_limit_history(history, limit_turn_n)

    user_intention_state_text, user_intention, user_state, user_topic = ai_chat.intention_status_analysis(
        chat_history=limit_history,
        user_question=user_question)

    # ---------------------
    # 实际说什么
    # ---------------------
    answer_text = ai_chat.question_response(last_summary=last_summary,
                                            latest_history=limit_history,
                                            current_user_question=user_question,
                                            user_state=user_state,
                                            user_intention=user_intention,
                                            user_topic=user_topic,
                                            role_robot=role_robot)

    history[-1][-1] = f"{role_robot}: {answer_text}"

    # ---------------------
    # 根据新的回复进行summary
    # ---------------------

    if len(history) > limit_turn_n * 2:
        chat_history = get_limit_history(history[:-limit_turn_n][-limit_turn_n:])
        history_summary = ai_chat.history_summary(chat_history=chat_history, last_summary=last_summary,
                                                  persona_name=role_robot)
    else:
        history_summary = None

    return history, user_intention_state_text, None, history_summary


def clear_def():
    return None


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# chain-of-thought 聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                limit_turn_n = gr.Slider(1, 10, step=1, value=2, label="保留的历史记录轮次", interactive=True)
                gpt_select = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Textbox(lines=1, value="Angelie", label="live robot name", interactive=False)

            user_intention_state = gr.Textbox(lines=3, value=None, label="用户意图状态分析", interactive=False)
            history_summary = gr.Textbox(lines=3, value=None, label="聊天历史总结",
                                         interactive=False)

            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

        with gr.Column():
            clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="history")

    user_input.submit(chat_f, [chatbot, user_input, history_summary, role_human, role_robot, limit_turn_n, gpt_select],
                      [chatbot, user_intention_state, user_input, history_summary], queue=False)

    clear.click(clear_def, inputs=[], outputs=[chatbot])

demo.queue().launch(server_name="0.0.0.0", server_port=8801)
