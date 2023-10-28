import gradio as gr
import config
import random
import time

from aipet import PersonPet

all_pet_names = list(config.pets_dic.keys())

# 初始化用户示例
glob_pet_obj: PersonPet = PersonPet(all_pet_names[0])


def get_history_str(history: list):
    if len(history) <= 0:
        return ''
    history_list = []
    for qa in history:
        for q_a in qa:
            if q_a is not None:
                history_list.append(q_a)
    return '\n'.join(history_list)


def chat_f(curr_time: str,
           current_state: str,
           history: list,
           pet_name: str,
           user_question: str,
           pet_question: str,
           plans: str
           ):
    """宠物和主人的聊天"""

    history.append([f"主人: {user_question}", None])

    pet_answer = glob_pet_obj.user_pet_chat(curr_time, current_state, user_question, pet_question,
                                            get_history_str(history), plans)

    history[-1][-1] = f"{pet_name}: {pet_answer}"

    return history, None


def get_pet_info_str(pet_name):
    """
    获取宠物信息
    """
    pet_info_list = []
    for k in config.pets_dic[pet_name]:
        pet_info_list.append(f"{k}: {config.pets_dic[pet_name][k]}")

    return '\n'.join(pet_info_list)


def get_place_info_str():
    place_list = []
    for k in config.places_dic:
        place_list.append(f"{k}: {config.places_dic[k]}")
    place_list_str = '\n'.join(place_list)

    return place_list_str


def get_push_message(current_time, current_state):
    """
    推送信息
    """
    return glob_pet_obj.push(curr_time=current_time, current_state=current_state)


def select_pet(pet_name, gpt_version):
    """
    选择宠物
    """
    global glob_pet_obj
    glob_pet_obj = PersonPet(name=pet_name, gpt_version=gpt_version)
    return get_pet_info_str(pet_name), None, None, None, None, None, None, None, None, None, None, None, None


def get_state(pet_name, curr_time, history_list: list):
    """
    获取宠物的状态
    """

    # --------------------
    # 状态
    # --------------------
    cur_state = glob_pet_obj.state(curr_time=curr_time)

    def get_value(key):
        for line in cur_state.split("\n"):
            if str(line).startswith(key):
                return line.replace(key, "").strip()

    pet_mood = get_value("心情:")
    pet_satiety = get_value("饱腹感:")
    pet_thought = get_value("思考:")
    pet_state = get_value("状态:")
    pet_local = get_value("位置:")

    # --------------------
    # 留言
    # --------------------
    leave_message = glob_pet_obj.leave_message(curr_time=curr_time, current_state=cur_state)
    history_list.append([f"{pet_name}: {leave_message}", None])

    # --------------------
    # 宠物接下来的计划
    # --------------------
    next_plan = glob_pet_obj.plan(current_state=cur_state, curr_time=curr_time)

    return pet_satiety, pet_mood, pet_local, cur_state, leave_message, history_list, next_plan


def give_feed(curr_time: str, cur_state: str, feed_type: str):
    # --------------------
    # 状态
    # --------------------
    cur_state = glob_pet_obj.give_feed(curr_time=curr_time, current_state=cur_state, feed_type=feed_type)

    def get_value(key):
        for line in cur_state.split("\n"):
            if str(line).startswith(key):
                return line.replace(key, "").strip()

    to_user_msg = get_value("对主人说:")
    pet_satiety = get_value("饱腹感:")
    pet_mood = get_value("心情:")
    pet_thought = get_value("思考:")
    pet_state = get_value("状态:")
    pet_local = get_value("位置:")

    return to_user_msg, pet_satiety, pet_mood, cur_state, pet_local


def summon_pet(pet_name: str, curr_time: str, cur_state: str, history: list):
    per_res = glob_pet_obj.summon(curr_time=curr_time, current_state=cur_state)

    history.append([f"{pet_name}: {per_res}", None])

    return per_res, history


def stroke_pet(curr_time: str, cur_state: str):
    per_res = glob_pet_obj.stroke(curr_time=curr_time, current_state=cur_state)

    return per_res


feed_type_list = ["萝卜", "草", "芒果", "香蕉", "水", "大蒜", "啤酒", "巧克力"]
stroke_type_list = ["头部", "肚子", "脚", "手", "背部", "鼻子"]

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# AI宠物聊天demo")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                current_time_txtbox = gr.Textbox(lines=1, value=time.strftime("%H:%M:%S", time.localtime()),
                                                 label="now time", interactive=True)
                gpt_select_dpd = gr.Dropdown(value='gpt3.5', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                             interactive=True)
                pet_select_dpd = gr.Dropdown(value=all_pet_names[0], choices=all_pet_names, label="领养你的宠物",
                                             interactive=True)
            with gr.Row():
                pet_info_txtbox = gr.Textbox(lines=2, value=get_pet_info_str(all_pet_names[0]), label="宠物信息",
                                             interactive=False)

                place_info_txtbox = gr.Textbox(lines=2, value=get_place_info_str(), label="可活动位置", interactive=False)

            pet_state_btn = gr.Button("点击获取宠物当前状态(模拟一段时间自动刷新宠物状态)")

            with gr.Row():
                with gr.Column():
                    stroke_type_dpd = gr.Dropdown(label="选择抚摸部位", value=stroke_type_list[0], choices=stroke_type_list,
                                                  interactive=True)
                    stroke_btn = gr.Button("抚摸")
                with gr.Column():
                    feed_type_dpd = gr.Dropdown(label="选择投喂的食物", value=feed_type_list[-1], choices=feed_type_list,
                                                interactive=True)
                    give_feed_btn = gr.Button("投喂")
                with gr.Column():
                    push_info_btn = gr.Button("推送信息")
                    summon_my_pet_btn = gr.Button("召唤宠物")

            with gr.Row():
                pet_satiety_txtbox = gr.Textbox(lines=1, value=None, label="宠物饱腹感", interactive=True)
                pet_mood_txtbox = gr.Textbox(lines=1, value=None, label="宠物心情", interactive=True)
                pet_local_txtbox = gr.Textbox(lines=1, value=None, label="宠物位置", interactive=True)

            with gr.Row():
                announcement_info_txtbox = gr.Textbox(lines=5, value=None, label="推送信息", interactive=True)
                with gr.Column():
                    pet_message_txtbox = gr.Textbox(lines=1, value=None, label="宠物留言", interactive=True)
                    pet_state_txtbox = gr.Textbox(lines=1, value=None, label="宠物当前状态", interactive=True)
                pet_plan_txtbox = gr.Textbox(lines=1, value=None, label="宠物的计划行程", interactive=True)

        with gr.Column():
            # clear = gr.Button("clean history")
            chatbot = gr.Chatbot(label="宠物跟主人的聊天历史", value=None)
            user_input = gr.Textbox(placeholder="input(Enter确定)", label="INPUT")

    user_input.submit(chat_f, inputs=[current_time_txtbox, pet_state_txtbox, chatbot, pet_select_dpd, user_input,
                                      pet_message_txtbox, pet_plan_txtbox],
                      outputs=[chatbot, user_input],
                      queue=False)

    # 点击获取宠物状态
    pet_state_btn.click(get_state, inputs=[pet_select_dpd, current_time_txtbox, chatbot],
                        outputs=[pet_satiety_txtbox, pet_mood_txtbox, pet_local_txtbox, pet_state_txtbox,
                                 pet_message_txtbox, chatbot, pet_plan_txtbox])

    # 点击推送
    push_info_btn.click(get_push_message, inputs=[current_time_txtbox, pet_state_txtbox],
                        outputs=[announcement_info_txtbox])

    # 重新选择宠物
    pet_select_dpd.change(select_pet, inputs=[pet_select_dpd, gpt_select_dpd],
                          outputs=[pet_info_txtbox, push_info_btn, summon_my_pet_btn, give_feed_btn, pet_satiety_txtbox,
                                   pet_mood_txtbox,
                                   pet_local_txtbox,
                                   announcement_info_txtbox, pet_message_txtbox, pet_plan_txtbox, chatbot, user_input])

    # 投喂
    give_feed_btn.click(give_feed, inputs=[current_time_txtbox, pet_state_txtbox, feed_type_dpd],
                        outputs=[announcement_info_txtbox, pet_satiety_txtbox, pet_mood_txtbox, pet_state_txtbox,
                                 pet_local_txtbox])

    # 主人召唤
    summon_my_pet_btn.click(summon_pet, inputs=[pet_select_dpd, current_time_txtbox, pet_state_txtbox, chatbot],
                            outputs=[announcement_info_txtbox, chatbot])

    # 主人抚摸
    stroke_btn.click(stroke_pet, inputs=[current_time_txtbox, pet_state_txtbox],
                     outputs=[announcement_info_txtbox])

demo.queue().launch(server_name="0.0.0.0", server_port=8700)
