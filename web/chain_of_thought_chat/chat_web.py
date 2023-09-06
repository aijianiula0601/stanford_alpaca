import gradio as gr
from aichat import ChainOfThoughtChat

ai_chat = ChainOfThoughtChat()


def get_limit_history(history: list[list], limit_turn_n=5):
    return '\n'.join([q_a for qa in history[limit_turn_n:] for q_a in qa])


def bot(history: list,
        user_question: str,
        last_summary: str,
        role_human: str = "user",
        role_robot: str = "robot",
        gpt_version: str = '4'):
    history.append([user_question, None])

    role_a = role_human + ": "
    role_b = role_robot + ": "

    # ---------------------
    # 重新设置环境
    # ---------------------
    ai_chat.set_role(role_robot)
    ai_chat.set_gpt_env(gpt_version)

    # ---------------------
    # 分析用户意图和状态
    # ---------------------
    user_intention_state_text, user_intention, user_state = ai_chat.intention_status_analysis(
        chat_history=get_limit_history(history),
        user_question=user_question)



    # ---------------------
    # 实际说什么
    # ---------------------
    answer_text = ai_chat.question_response(last_summary=last_summary,
                                            latest_history=get_limit_history(history, limit_turn_n=5),
                                            current_user_question=user_question,
                                            user_state=user_state,
                                            user_intention=user_intention)

    history[-1][-1] = role_b + answer_text


    # ---------------------
    # 根据新的回复进行summary
    # ---------------------
    # robot_summary, cost_time = ai_chat.summarize_chat(robot_summary, history[-1])

    return history, user_intention_state_text


def clear_def():
    return None


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# chain-of-thought 聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Textbox(lines=1, value="Angelie", label="live robot name", interactive=False)

            user_intention_state = gr.Textbox(lines=3, value=None, label="用户意图状态分析", interactive=False)
            history_summary = gr.Textbox(lines=3, value="Angelie want to chat with the user.", label="聊天历史总结",
                                         interactive=False)

            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

        with gr.Column():
            clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="history")

    user_input.submit(bot, [chatbot, user_input, history_summary, role_human, role_robot],
                      [chatbot, user_intention_state], queue=False)

    clear.click(clear_def, inputs=[], outputs=[chatbot])

demo.queue().launch(server_name="0.0.0.0", server_port=8801)
