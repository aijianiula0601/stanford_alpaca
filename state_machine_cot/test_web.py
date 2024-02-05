import gradio as gr
from aichat_state import AIChat
import prompt
import json
import random
import logging
import importlib

readme_str = ''.join(open('README.md', 'r').readlines())

all_role_name_list = list(prompt.state_cot_config['state_v6_base']['PERSONA_DICT'].keys())

greeting_data = json.load(open('greeting.json', 'r'))

logging.basicConfig(format='%(message)s', level=logging.INFO)
ai_chat_obj = AIChat('rosa')


def get_initialize_greet_text():
    return random.sample(greeting_data['first_day'], k=1)[0]


def get_second_day_greet_text():
    return random.sample(greeting_data['second_day'], k=1)[0]


def init_story_topics(role_name):
    """
    函数功能：初始化话题列表。
    详细说明：
     - 话题列表是供telling状态使用的，当进入telling状态后，会从话题列表中选择话题，将对应的故事放到telling状态的prompt里
     - data是一个存放所有话题的字典，每个话题作为key，而value中第一个元素是一个数值，代表亲密度到达多少时会解锁该话题。第二个元素是故事本身。
     - 用户在第一天时解锁数值为0的话题，在第二天时解锁数值为60的话题。平时聊天中亲密度也会越来越高，解锁的话题越来越多，实现剧情推进。
    """

    story_topics = []
    data = prompt.state_cot_config['state_v6_base']['STORY_DICT']
    for t in data:
        if data[t][0] == 0:
            story_topics.append(t)
            data[t][1] = data[t][1].format_map({'name': role_name})

    return story_topics, data


def init_second_day_story_topics(role_name):
    story_topics = []
    data = prompt.state_cot_config['state_v6_base']['STORY_DICT']
    for t in data:
        if data[t][0] == 60:
            story_topics.append(t)
            data[t][1] = data[t][1].format_map({'name': role_name})

    return story_topics, data


def init():
    role_name = 'rosa'
    greeting_text = get_initialize_greet_text()

    user_vars = {
        'robot_role_attr': {
            'robot_nickname': role_name
        },
        'history': [[None, f"{role_name}: {greeting_text}"]],
        'history_with_pic': [[None, f"{role_name}: {greeting_text}"]],
        'day': 1,
        'intimacy_score': 5,
        'state_history': [],
        'story_topics': (init_story_topics(role_name))[0],
        'story_data': (init_story_topics(role_name))[1]
    }
    return user_vars


def init_second():
    role_name = 'rosa'
    greeting_text = get_second_day_greet_text()

    user_vars = {
        'robot_role_attr': {
            'robot_nickname': role_name
        },
        'history': [[None, f"{role_name}: {greeting_text}"]],
        'history_with_pic': [[None, f"{role_name}: {greeting_text}"]],
        'day': 2,
        'intimacy_score': 60,
        'state_history': [],
        'story_topics': (init_second_day_story_topics(role_name))[0],
        'story_data': (init_second_day_story_topics(role_name))[1]}
    ai_chat_obj.greeting_rounds = 6
    return user_vars


def clear_f():
    user_vars = init()
    importlib.reload(prompt)
    return user_vars['history_with_pic'], None, None, None, None, user_vars


def another_day_f():
    user_vars = init_second()
    return user_vars['history_with_pic'], None, None, None, None, user_vars


def gpt_version_f(gpt_version):
    ai_chat_obj.gpt_version = gpt_version


def chat_f(user_question, role_robot, user_vars, user_language_code):
    round_num = len(user_vars['history'])

    answer_text, _, _, new_history, new_history_with_pic, new_intimacy_score, new_state_history, new_story_topics, _, key_info = ai_chat_obj.chat_main(
        round_num=round_num,
        history=user_vars['history'],
        history_with_pic=user_vars['history_with_pic'],
        user_question=user_question,
        openai_config=None,
        robot_role_attr=user_vars['robot_role_attr'],
        cur_time=None,
        exp_tag="state_v6_base",
        robot_uid=role_robot,
        user_uid="user",
        user_language_code=user_language_code,
        day=user_vars['day'],
        old_intimacy_score=user_vars['intimacy_score'],
        story_topics=user_vars['story_topics'],
        story_data=user_vars['story_data'],
        last_state_history=user_vars['state_history'],
        send_pic_flag=True,
        role_robot=role_robot
    )

    user_vars['history'] = new_history
    user_vars['history_with_pic'] = new_history_with_pic
    user_vars['intimacy_score'] = new_intimacy_score
    user_vars['state_history'] = new_state_history
    user_vars['story_topics'] = new_story_topics

    internal_info = ("round: {}\n"
                     "current_state: {}\n"
                     "day: {}\n"
                     "intimacy: {}\n"
                     "story_topics_remaining: [{}]\n"
                     "---------- state sequence ----------\n"
                     "{}"
                     ).format(round_num, user_vars['state_history'][-1], user_vars['day'], user_vars['intimacy_score'], ", ".join(user_vars['story_topics']), '->'.join(user_vars['state_history']))
    return user_vars['history_with_pic'], None, internal_info, None, None, user_vars


with gr.Blocks() as demo:
    user_vars = gr.State(value=init())
    with gr.Row():
        gr.Markdown("# State machine demo v6_base 基础聊天体验")
    with gr.Row():
        with gr.Column():
            readme = gr.Textbox(lines=1, value=readme_str, label="README.md", interactive=True)
            with gr.Row():
                role_robot = gr.Dropdown(value=all_role_name_list[0], choices=all_role_name_list, label="角色选择", interactive=True)
                user_language_code = gr.Dropdown(value='Chinese', choices=['English', 'Chinese', 'Spanish', 'Bengali', 'Arabic'], label="语言选择", interactive=True)
                # gpt_version = gr.Dropdown(value='3.5', choices=['3.5', 'gpt4'], label="gpt版本", interactive=True)

            machine_state = gr.Textbox(lines=1, value=None, label="内在状态", interactive=True)
            intention_analysis = gr.Textbox(lines=3, value=None, label="意图分析", interactive=False)
            history_summary = gr.Textbox(lines=3, value=None, label="结构化记忆", interactive=False)

        with gr.Column():
            with gr.Row():
                clear = gr.Button("clean history")
                another_day = gr.Button("Another day")

            chat_bot = gr.Chatbot(label="history", value=[[None, user_vars.value['history'][0][1]]], height=600)
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input.submit(chat_f,
                      [user_input, role_robot, user_vars, user_language_code],
                      [chat_bot, user_input, machine_state, intention_analysis, history_summary, user_vars],
                      queue=False)

    # gpt_version.change(gpt_version_f, inputs=[gpt_version])

    clear.click(clear_f, inputs=[],
                outputs=[chat_bot, user_input, machine_state, intention_analysis, history_summary, user_vars])
    role_robot.change(clear_f, inputs=[],
                      outputs=[chat_bot, user_input, machine_state, intention_analysis, history_summary, user_vars])
    another_day.click(another_day_f, inputs=[],
                      outputs=[chat_bot, user_input, machine_state, intention_analysis, history_summary, user_vars])

demo.queue().launch(server_name="0.0.0.0", server_port=8887)
