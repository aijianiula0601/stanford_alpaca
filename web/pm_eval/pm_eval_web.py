import os
import sys
import gradio as gr

pjd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pjd}")
sys.path.append(pjd)

from web.bigolive_onlive.web_chat import get_input_api_data, mask_instruct, get_history

default_background = "let's play a role game. Angelie is a unknown, Aries, lives in Liwa. Angelie's occupation is Physician Assistant, her personality is INFP, her favorite sport is Skateboarding, her favorite movie genre is Rom-com, her favorite music genre is Pop, and her favorite book is Comic books. now you will play the role of Angelie, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people."


def get_model1_answer(history, user_question, role_a_name, role_b_name, selected_temp=0.7):
    history = history + [[f"{role_a_name}: " + user_question, None]]

    model_input_api_data = get_input_api_data(background=f"{default_background}",
                                              history=get_history(role_a_name, role_b_name, history),
                                              history_limit_turns=3)

    model_answer = mask_instruct(model_input_api_data, temperature=selected_temp)

    return model_answer


def get_model2_answer(history, user_question, role_a_name, role_b_name, selected_temp=0.7):
    history = history + [[f"{role_a_name}: " + user_question, None]]

    model_input_api_data = get_input_api_data(background=f"{default_background}",
                                              history=get_history(role_a_name, role_b_name, history),
                                              history_limit_turns=3)

    model_answer = mask_instruct(model_input_api_data, temperature=selected_temp)

    return model_answer


def chat_f(history, user_question, role_human, role_bot, selected_temp=0.7):
    # model1_answer = get_model1_answer(history, user_question, role_human, role_bot, selected_temp)
    # model2_answer = get_model1_answer(history, user_question, role_human, role_bot, selected_temp)

    model1_answer = "Hello! How are you today?111"
    model2_answer = "Hello! How are you today?222"

    history += [[f"{role_human}: " + user_question, f"{role_bot}(model1):{model1_answer}"]]
    history += [[None, f"{role_bot}(model1):{model2_answer}"]]

    return history


def choice_btn_click(approve_oppose, history):
    choice_answer = None

    if history and len(history) >= 2:

        if history[-1][0] is not None:
            raise gr.Error('no answer to choose!')

        model_1_answer = history[-2][-1]
        model_2_answer = history[-1][-1]

        if approve_oppose == "model1👍":
            choice_answer = model_1_answer
        if approve_oppose == "model2👍":
            choice_answer = model_2_answer

    return f"submit({approve_oppose})", choice_answer


def vote_submit_click(choice_answer, history, role_bot):
    if choice_answer.strip() == "":
        raise gr.Error('must choice a answer!')

    if history and len(history) >= 2:
        question = history[-2][0]
        history = history[:-2]
        history += [[question, f"{role_bot}: {choice_answer}"]]

    return history, ""


def clear_def():
    return None, None, None


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# pair models eval demo")

    with gr.Row():
        with gr.Column():
            your_name = gr.Textbox(label="your name", placeholder="please input your name", interactive=True)

            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Textbox(lines=1, value="Angelie", label="robot name", interactive=False)

            background = gr.Textbox(lines=3, value=None, label="Personal information", interactive=False)

            user_input = gr.Textbox(placeholder="input(Enter)", label="INPUT")

        with gr.Column():
            clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="history")
            choice_answer = gr.Textbox(lines=1, label="selected answer", interactive=False)
            with gr.Row():
                model1_vote_btn = gr.Button(value="model1👍")
                model2_vote_btn = gr.Button(value="model2👍")

            choice_btn = gr.Button("submit")

    model1_vote_btn.click(choice_btn_click, [model1_vote_btn, chatbot], [choice_btn, choice_answer])
    model2_vote_btn.click(choice_btn_click, [model2_vote_btn, chatbot], [choice_btn, choice_answer])

    user_input.submit(chat_f, [chatbot, user_input, role_human, role_robot], [chatbot])
    choice_btn.click(vote_submit_click, [choice_answer, chatbot, role_robot], [chatbot, choice_answer])

demo.queue().launch(server_name="0.0.0.0", server_port=7801)
