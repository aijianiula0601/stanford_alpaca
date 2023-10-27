import gradio as gr
import config
import random
import time

all_pet_names = list(config.pets_dic.keys())


def chat_f(history: list,
           user_question: str,
           user_status: str,
           role_human: str = "user",
           role_robot: str = "robot",
           limit_turn_n: int = 5,
           gpt_version: str = 'gpt3.5',
           ):
    history.append([f"{role_human}: {user_question}", None])


def clear_f(role_human, role_robot):
    # 初始化机器人主动打招呼问候语

    return None, None, None, None, None


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# AI宠物聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                limit_turn_n = gr.Slider(1, 10, step=1, value=5, label="保留的历史记录轮次", interactive=True)
                gpt_select = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True)
                role_pet = gr.Dropdown(value=all_pet_names[-1], choices=all_pet_names, label="领养你的宠物",
                                       interactive=True)

            pet_info = gr.Textbox(lines=2, value=None, label="宠物信息", interactive=False)
            with gr.Row():
                summon_my_pet = gr.Button("召唤宠物")
                give_feed = gr.Button("投喂")
                # pet_message = gr.Button("宠物的留言")

            with gr.Row():
                pet_state = gr.Textbox(lines=1, value=None, label="宠物状态", interactive=True)
                pet_mood = gr.Textbox(lines=1, value=None, label="宠物心情", interactive=True)

            with gr.Row():
                pet_message = gr.Textbox(lines=1, value=None, label="宠物留言", interactive=True)
                pet_plan = gr.Textbox(lines=1, value=None, label="宠物的计划行程", interactive=True)

        with gr.Column():
            with gr.Row():
                clear = gr.Button("clean history")

            chatbot = gr.Chatbot(label="宠物跟主人的聊天历史", value=None)
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input.submit(chat_f, [chatbot, user_input, pet_state, role_pet,
                               limit_turn_n, gpt_select],
                      [chatbot, user_input, pet_state],
                      queue=False)

    clear.click(clear_f, inputs=[role_pet],
                outputs=[chatbot, pet_state])
    role_pet.change(clear_f, inputs=[role_pet],
                    outputs=[chatbot, pet_state])

demo.queue().launch(server_name="0.0.0.0", server_port=8808)
