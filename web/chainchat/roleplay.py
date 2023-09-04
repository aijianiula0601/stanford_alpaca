import json
import random
import time
from datetime import datetime
from tqdm import tqdm
import requests
from typing import List, Tuple
from copy import deepcopy
import types
# import asyncio

import os

import gradio as gr
from ai_chat_roleplay import *


def user(user_message, history, roleA):
    human_invitation = roleA + ": "
    return "", history + [[human_invitation + user_message, None]]


def bot(history, robot_plan, robot_summary, role_human="user", role_robot="robot", jailbreak=True, if_gpt4=False):
    role_a = role_human + ": "
    role_b = role_robot + ": "

    # 计划说什么
    robot_plan, cost_time, thinking_txt = ai_chat.memory_plan(robot_summary, history[-1][0].replace(role_a, ""),
                                                              jailbreak, if_gpt4)

    # 实际说什么
    tmp_output, cost_time = ai_chat.plan_then_say(robot_summary, robot_plan, history[-1][0].replace(role_a, ""),
                                                  jailbreak, if_gpt4)
    history[-1][-1] = role_b + tmp_output
    # 根据新的回复进行summary
    robot_summary, cost_time = ai_chat.summarize_chat(robot_summary, history[-1])

    print(stat)

    if if_gpt4:
        price_cost = round(stat["total_use"] / 1000 * 0.06, 5)
    else:
        price_cost = round(stat["total_use"] / 1000 * 0.002, 5)

    return history, robot_plan, robot_summary, price_cost, thinking_txt


def clear_def():
    ai_chat.__init__()
    stat["total_call"] = 0
    stat["total_use"] = 0

    return None


with gr.Blocks() as demo:
    ai_chat = AIChat()
    with gr.Row():
        gr.Markdown("# 聊天机器人Prompt demo 请使用英语测试")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                role_human = gr.Textbox(lines=1, value="user", label="human name", interactive=False)
                role_robot = gr.Textbox(lines=1, value="Angelie", label="live robot name", interactive=False)

            with gr.Row():
                price_total = gr.Textbox(lines=1, value="0", label="花费（美元）", interactive=False)
                if_jailbreak = gr.Checkbox(value=True, label="是否越狱")
                if_gpt4 = gr.Checkbox(value=False, label="是否使用gpt4")

            robot_thinking = gr.Textbox(lines=3, value="chat", label="机器人在想什么", interactive=False)
            robot_plan = gr.Textbox(lines=3, value="Say hello", label="chat topic", interactive=False)
            robot_summary = gr.Textbox(lines=3, value="Angelie want to chat with the user.", label="chat summary",
                                       interactive=False)

            msg = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

            # BEGIN = gr.Button("DEMO begin",variant="primary")
        with gr.Column():
            # time_out = gr.Button("DEBUG: 机器人尝试多次回复")
            clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="history")

    msg.submit(user, [msg, chatbot, role_human],
               [msg, chatbot], queue=False).then(
        bot, [chatbot, robot_plan, robot_summary, role_human, role_robot, if_jailbreak, if_gpt4],
        [chatbot, robot_plan, robot_summary, price_total, robot_thinking], queue=False
    )

    # clear.click(lambda: None, None, chatbot, queue=False)
    clear.click(clear_def, inputs=[], outputs=[chatbot])

# demo.queue().launch()
demo.queue().launch(server_name="0.0.0.0", server_port=8101)
