import os
import sys
import gradio as gr
import time
import datetime

pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pjd}")
sys.path.append(pjd)

from web.bigolive_onlive.web_chat import get_message_list, mask_instruct, get_history

default_background = "let's play a role game. Angelie is a unknown, Aries, lives in Liwa. Angelie's occupation is Physician Assistant, her personality is INFP, her favorite sport is Skateboarding, her favorite movie genre is Rom-com, her favorite music genre is Pop, and her favorite book is Comic books. now you will play the role of Angelie, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people."


def get_model1_answer(history, user_question, role_a_name, role_b_name, selected_temp=0.7):
    history = history + [[f"{role_a_name}: " + user_question, None]]

    model_input_api_data = get_message_list(background=f"{default_background}",
                                            history=get_history(role_a_name, role_b_name, history),
                                            history_limit_turns=3)

    model_answer = mask_instruct(model_input_api_data, temperature=selected_temp)

    return model_answer


def get_model2_answer(history, user_question, role_a_name, role_b_name, selected_temp=0.7):
    history = history + [[f"{role_a_name}: " + user_question, None]]

    model_input_api_data = get_message_list(background=f"{default_background}",
                                            history=get_history(role_a_name, role_b_name, history),
                                            history_limit_turns=3)

    model_answer = mask_instruct(model_input_api_data, temperature=selected_temp)

    return model_answer


def chat_f(your_name, history, user_question, role_human, role_bot, last_choice_answer, selected_temp=0.7):
    if your_name.strip() == "":
        raise gr.Error('your_name must input!')

    # --------------------
    # 获取选择的answer
    # --------------------
    if history and len(history) >= 2:
        if history[-1][0] is not None or last_choice_answer.strip() == "":
            raise gr.Error('no answer to choose!')

        last_question = history[-2][0]
        history = history[:-2] + [[last_question, f"{role_bot}: {last_choice_answer}"]]

    # model1_answer = get_model1_answer(history, user_question, role_human, role_bot, selected_temp)
    # model2_answer = get_model1_answer(history, user_question, role_human, role_bot, selected_temp)
    model1_answer = "Hello! How are you today?111"
    model2_answer = "Hello! How are you today?222"

    history += [[f"{role_human}: " + user_question, f"{role_bot}(model1): {model1_answer}"]]
    history += [[None, f"{role_bot}(model2): {model2_answer}"]]

    return history, ""


def get_choice_answer(approve_oppose, history):
    choice_answer = None

    if history and len(history) >= 2:

        if history[-1][0] is not None:
            raise gr.Error('no answer to choose!')

        model_1_answer = history[-2][-1].split("): ")[-1]
        model_2_answer = history[-1][-1].split("): ")[-1]

        if approve_oppose == "model1👍":
            choice_answer = model_1_answer
        if approve_oppose == "model2👍":
            choice_answer = model_2_answer

    return choice_answer


def your_name_input_f(your_name):
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return f"{your_name}#{now_time}"



def clear_def():
    return None, None, None


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# pair models eval demo")

    with gr.Row():
        with gr.Column():
            with gr.Row():
                your_name = gr.Textbox(label="your name", placeholder="please input your name", interactive=True)
                dialogue_id = gr.Textbox(label="dialogue id", interactive=False)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Textbox(lines=1, value="Angelie", label="robot name", interactive=False)

            background = gr.Textbox(lines=4, value=None, label="Personal information", interactive=False)

            user_input = gr.Textbox(placeholder="input(Enter)", label="INPUT")
            dialogues_submit_btn = gr.Button(value="submit dialogues")

        with gr.Column():
            clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="history")
            choice_answer = gr.Textbox(lines=1, label="selected answer", interactive=False)
            with gr.Row():
                model1_vote_btn = gr.Button(value="model1👍")
                model2_vote_btn = gr.Button(value="model2👍")

    model1_vote_btn.click(get_choice_answer, [model1_vote_btn, chatbot], [choice_answer])
    model2_vote_btn.click(get_choice_answer, [model2_vote_btn, chatbot], [choice_answer])

    user_input.submit(chat_f, [your_name, chatbot, user_input, role_human, role_robot, choice_answer],
                      [chatbot, choice_answer])
    your_name.submit(your_name_input_f, your_name, dialogue_id)

demo.queue().launch(server_name="0.0.0.0", server_port=7801)
