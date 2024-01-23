import gradio as gr
import json
import random
import logging
import importlib
import json

# ---------------------
# 初始化
# ---------------------
ALL_ROLE_NAME_LIST = list(json.load(open("profiles/roles.json", 'r', encoding="utf-8")).keys())
GREETING_DATA_DIC = json.load(open('data/greeting.json', 'r'))



aichat = AIChat('rosa')

#
# def get_initialize_greet_text():
#     return random.sample(greeting_data['first_day'], k=1)[0]
#
#
# def get_second_day_greet_text():
#     return random.sample(greeting_data['second_day'], k=1)[0]
#
#
# def init_story_topics(role_name):
#     story_topics = []
#     data = config_state_cot.state_cot_config['state_v5_bot']['STORY_DICT']
#     for t in data:
#         if data[t][0] == 0:
#             story_topics.append(t)
#             data[t][1] = data[t][1].format_map({'name': role_name})
#
#     return story_topics, data
#
#
# def init_secondday_story_topics(role_name):
#     story_topics = []
#     data = config_state_cot.state_cot_config['state_v5_bot']['STORY_DICT']
#     for t in data:
#         if data[t][0] == 60:
#             story_topics.append(t)
#             data[t][1] = data[t][1].format_map({'name': role_name})
#
#     return story_topics, data
#
#
# def init():
#     role_name = 'rosa'
#     greeting_text = get_initialize_greet_text()
#
#     user_vars = {
#         'robot_role_attr': {'robot_nickname': role_name},
#         'history': [[None, f"{role_name}: {greeting_text}"]],
#         'history_with_pic': [[None, f"{role_name}: {greeting_text}"]],
#         'day': 1,
#         'intimacy_score': 5,
#         'state_history': [],
#     }
#     user_vars['story_topics'], user_vars['story_data'] = init_story_topics(role_name)
#     return user_vars
#
#
# def init_second():
#     role_name = 'rosa'
#     greeting_text = get_second_day_greet_text()
#
#     user_vars = {
#         'robot_role_attr': {'robot_nickname': role_name},
#         'history': [[None, f"{role_name}: {greeting_text}"]],
#         'history_with_pic': [[None, f"{role_name}: {greeting_text}"]],
#         'day': 2,
#         'intimacy_score': 60,
#         'state_history': [],
#     }
#     user_vars['story_topics'], user_vars['story_data'] = init_secondday_story_topics(role_name)
#     aichat.greeting_rounds = 6
#     return user_vars
#
#
# def clear_f():
#     user_vars = init()
#     importlib.reload(config_state_cot)
#     return user_vars['history_with_pic'], None, None, None, None, user_vars
#
#
# def another_day_f():
#     user_vars = init_second()
#     return user_vars['history_with_pic'], None, None, None, None, user_vars
#
#
# def chat_f(user_question, role_robot, user_vars):
#     round_num = len(user_vars['history'])
#
#     answer_text, \
#     _, \
#     _, \
#     new_history, \
#     new_history_with_pic, \
#     new_intimacy_score, \
#     new_state_history, \
#     new_story_topics, \
#     _, \
#     key_info \
#         = aichat.chat_main(
#         round_num=round_num,
#         history=user_vars['history'],
#         history_with_pic=user_vars['history_with_pic'],
#         user_question=user_question,
#         openai_config=None,
#         robot_role_attr=user_vars['robot_role_attr'],
#         cur_time=None,
#         exp_tag="state_v5_bot",
#         robot_uid=role_robot,
#         user_uid="user",
#         user_language_code=None,
#         day=user_vars['day'],
#         old_intimacy_score=user_vars['intimacy_score'],
#         story_topics=user_vars['story_topics'],
#         story_data=user_vars['story_data'],
#         last_state_history=user_vars['state_history'],
#         send_pic_flag=True,
#         role_robot=role_robot
#     )
#
#     user_vars['history'] = new_history
#     user_vars['history_with_pic'] = new_history_with_pic
#     user_vars['intimacy_score'] = new_intimacy_score
#     user_vars['state_history'] = new_state_history
#     user_vars['story_topics'] = new_story_topics
#
#     internal_info = ("round: {}\n"
#                      "current_state: {}\n"
#                      "day: {}\n"
#                      "intimacy: {}\n"
#                      "story_topics_remaining: [{}]\n"
#                      "---------- state sequence ----------\n"
#                      "{}"
#                      ).format(round_num, user_vars['state_history'][-1], user_vars['day'], user_vars['intimacy_score'], ", ".join(user_vars['story_topics']), '->'.join(user_vars['state_history']))
#     return user_vars['history_with_pic'], None, internal_info, None, None, user_vars
#
#
# with gr.Blocks() as demo:
#     user_vars = gr.State(value=init())
#     with gr.Row():
#         gr.Markdown("# State machine demo v5.2_bot 以朋友身份推荐直播")
#     with gr.Row():
#         with gr.Column():
#             with gr.Row():
#                 role_robot = gr.Dropdown(value=ALL_ROLE_NAME_LIST[0], choices=ALL_ROLE_NAME_LIST, label="角色选择", interactive=True)
#
#             machine_state = gr.Textbox(lines=1, value=None, label="内在状态", interactive=True)
#             intention_analysis = gr.Textbox(lines=3, value=None, label="意图分析", interactive=False)
#             history_summary = gr.Textbox(lines=3, value=None, label="结构化记忆", interactive=False)
#
#         with gr.Column():
#             with gr.Row():
#                 clear = gr.Button("clean history")
#                 another_day = gr.Button("Another day")
#
#             chatbot = gr.Chatbot(label="history", value=[[None, user_vars.value['history'][0][1]]], height=600)
#             user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")
#
#     user_input.submit(chat_f,
#                       [user_input, role_robot, user_vars],
#                       [chatbot, user_input, machine_state, intention_analysis, history_summary, user_vars],
#                       queue=False)
#
#     clear.click(clear_f, inputs=[],
#                 outputs=[chatbot, user_input, machine_state, intention_analysis, history_summary, user_vars])
#     role_robot.change(clear_f, inputs=[],
#                       outputs=[chatbot, user_input, machine_state, intention_analysis, history_summary, user_vars])
#     another_day.click(another_day_f, inputs=[],
#                       outputs=[chatbot, user_input, machine_state, intention_analysis, history_summary, user_vars])
#
# demo.queue().launch(server_name="0.0.0.0", server_port=8887)
