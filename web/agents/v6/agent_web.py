import re
import time
import gradio as gr
import config
import random
from aipet import PersonPet
from openai_image_demo import prompt2img

all_pet_names = list(config.pets_dic.keys())

# 初始化用户示例
default_pet_name = all_pet_names[0]
glob_pet_obj: PersonPet = PersonPet(default_pet_name)

feed_type_list = ["萝卜", "草", "芒果", "香蕉", "水", "大蒜", "啤酒", "巧克力"]
stroke_type_list = ["头部", "肚子", "脚", "手", "背部", "鼻子"]
time_list = ["00:00:00", "01:00:00", "02:00:00", "03:00:00", "04:00:00", "05:00:00", "06:00:00", "07:00:00", "08:00:00",
             "09:00:00", "10:00:00", "11:00:00", "12:00:00", "13:00:00", "14:00:00", "15:00:00", "16:00:00",
             "17:00:00", "18:00:00", "19:00:00", "20:00:00", "21:00:00", "22:00:00", "23:00:00", "24:00:00"]

friend_state_list = [
    "已经隔了一天没来投喂了",
    "已经隔很久没来逗宠物玩了",
]


def parse_res_text(res_text: str, key: str):
    pattern = r'"{0}"\s*:\s*("[^"]*"|[^",]*)'.format(key)
    # pattern = r'"{0}"：\s*"([^"]*)"'.format(key)

    match = re.search(pattern, res_text)
    if match:
        value = match.group(1)
        return value
    else:
        pattern = r'"{0}"\s*：\s*("[^"]*"|[^",]*)'.format(key)
        match = re.search(pattern, res_text)
        if match:
            value = match.group(1)
            return value
        else:
            return None


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


def select_pet(pet_name, gpt_version):
    """
    选择宠物
    """
    global glob_pet_obj
    glob_pet_obj = PersonPet(name=pet_name)
    return get_pet_info_str(pet_name), None, None, None, None, None, None, None, time.strftime("%H:00:00",
                                                                                               time.localtime()), \
           stroke_type_list[0], \
           feed_type_list[0], None


def get_state_value(key, cur_state):
    for line in cur_state.split("\n"):
        if str(line).startswith(key) or str(line).startswith(f"{key}："):
            return line.replace(f"{key}:", "").replace(f"{key}：", "").strip()


def get_state(curr_time: str, pet_satiety_txtbox: str, cur_state: str, day_plan: str = None,
              displace_info_txtbox: str = None, friend_pet_state_txtbox: str = None, journey_rad: str = None,
              sample_destination=None):
    """
    获取宠物的状态
    """
    # --------------------
    # 时间推进一个小时
    # --------------------
    next_time = time_list[(time_list.index(curr_time) + 2) % len(time_list)]
    curr_time = time_list[(time_list.index(curr_time) + 1) % len(time_list)]

    # --------------------
    # 宠物接下来的计划
    # --------------------
    if day_plan is None or day_plan == '':
        sample_destination = random.sample(config.journey_places, k=1)[0]
        attraction_places = ','.join(config.attraction_dic[sample_destination])
        day_plan = glob_pet_obj.day_plan(journey_rad, sample_destination, attraction_places)

    # --------------------
    # 状态
    # --------------------
    res_text = glob_pet_obj.state(curr_time=curr_time, next_time=next_time, day_plan=day_plan, cur_state=cur_state,
                                  friend_cur_state=friend_pet_state_txtbox, journey_rad=journey_rad,
                                  cur_satiety=pet_satiety_txtbox, destination=sample_destination)

    pet_mood = parse_res_text(res_text, "心情")
    pet_satiety = parse_res_text(res_text, "饱腹感")
    pet_thought = parse_res_text(res_text, "思考")
    pet_cur_state = parse_res_text(res_text, "当前状态")
    next_plan = parse_res_text(res_text, "下一步计划")
    pet_local = parse_res_text(res_text, "位置")
    pet_say2master = parse_res_text(res_text, "对主人说")

    displace_state = f"【状态】{pet_cur_state}\n【思考】{pet_thought}\n【下一步计划】{next_plan}"

    pet_generate_pic = parse_res_text(res_text, "是否生成图片")
    pet_pic_prompt = parse_res_text(res_text, "图片描述")

    if journey_rad:
        if pet_generate_pic is not None and '生成景点图片' in pet_generate_pic:
            if 'None' not in pet_pic_prompt:
                prompt = '你是一只兔子宠物，你现在面对的场景是：\n'+pet_pic_prompt
        else:
            prompt = None

    # --------------------
    # 组装公告信息
    # --------------------
    if displace_info_txtbox is None or displace_info_txtbox == "":
        public_screen_str = f"【{curr_time}】【状态】{pet_cur_state}【思考】{pet_thought}【下一步计划】{next_plan}"
    else:
        public_screen_str = f"{displace_info_txtbox}\n【{curr_time}】【状态】{pet_cur_state}【思考】{pet_thought}【下一步计划】{next_plan}"

    # --------------------
    # 存入状态记忆
    # --------------------
    # state_memory = f"时间:{curr_time}\t{pet_cur_state}"
    # glob_pet_obj.day_state_memory_list.append(state_memory)

    # --------------------
    # 对一天所有状态进行总结
    # --------------------
    # 需要确定什么情况下
    # summary_day_state = glob_pet_obj.summary_day_state()

    # --------------------
    # 显示图片
    # --------------------
    journey_img_url = None
    if prompt is not None:
            journey_img_url = prompt2img(prompt=prompt)
    else:
        journey_img_url = None

    return pet_satiety, pet_mood, pet_local, displace_state, next_plan, pet_say2master, day_plan, curr_time, public_screen_str, cur_state, None, journey_img_url, sample_destination


def give_feed(curr_time: str, cur_state: str, feed_type: str, public_screen_txtbox: str = None):
    """
    投喂
    """
    # --------------------
    # 状态
    # --------------------
    next_time = time_list[(time_list.index(curr_time) + 1) % len(time_list)]
    cur_state = glob_pet_obj.give_feed(curr_time=curr_time, next_time=next_time, current_state=cur_state,
                                       feed_type=feed_type)

    to_user_msg = get_state_value("回应主人", cur_state)
    pet_satiety = get_state_value("饱腹感", cur_state)
    pet_mood = get_state_value("心情", cur_state)
    next_plan = get_state_value("下一步计划", cur_state)
    pet_local = get_state_value("位置", cur_state)
    pet_thought = get_state_value("思考", cur_state)
    pet_state = get_state_value("状态", cur_state)

    displace_state = f"【回应主人】{to_user_msg}\n【状态】{pet_state}\n【思考】{pet_thought}\n【下一步计划】{next_plan}"

    # --------------------
    # 组装公告信息
    # --------------------
    if public_screen_txtbox is None or public_screen_txtbox == "":
        public_screen_str = f"【{curr_time}】【投喂】{feed_type}【回应主人】{to_user_msg}"
    else:
        public_screen_str = f"{public_screen_txtbox}\n【{curr_time}】【投喂】{feed_type}【回应主人】{to_user_msg}"

    # --------------------
    # 更新隐藏的状态
    # --------------------
    hidden_state = f"饱腹感：{pet_satiety}\n心情：{pet_mood}\n思考：{pet_thought}\n状态：{pet_state}\n下一步计划：{next_plan}"

    return pet_satiety, pet_mood, displace_state, pet_local, next_plan, public_screen_str, hidden_state


def stroke_pet(curr_time: str, cur_state: str, stroke_type: str, pet_satiety: str, displace_info_txtbox: str,
               day_plan: str):
    """
    抚摸
    """

    def get_here_state_value(key, cur_state):
        for line in cur_state.split("\n"):
            if str(line).startswith(key):
                return line.replace(f"{key}", "").strip()

    next_time = time_list[(time_list.index(curr_time) + 2) % len(time_list)]

    next_plan = get_here_state_value("【下一步计划】", cur_state)
    pet_state = get_here_state_value("【状态】", cur_state)
    pet_thought = get_here_state_value("【思考】", cur_state)

    cur_state = glob_pet_obj.stroke(curr_time=curr_time, current_state=cur_state, stroke_type=stroke_type,
                                    next_time=next_time, day_plan=day_plan)

    per_res = get_state_value("回应主人", cur_state)
    pet_mood = get_state_value("心情", cur_state)

    # --------------------
    # 组装公告信息
    # --------------------
    if displace_info_txtbox is None or displace_info_txtbox == "":
        public_screen_str = f"【{curr_time}】【抚摸】{stroke_type}【回应主人】{per_res}"
    else:
        public_screen_str = f"{displace_info_txtbox}\n【{curr_time}】【抚摸】{stroke_type}【回应主人】{per_res}"

    displace_state = f"【回应主人】{per_res}\n【状态】{pet_state}\n【思考】{pet_thought}\n【下一步计划】{next_plan}"

    return displace_state, public_screen_str, pet_mood, pet_satiety


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# AI宠物聊天demo")
    with gr.Column():
        with gr.Row():
            pet_select_dpd = gr.Dropdown(value=default_pet_name, choices=all_pet_names, label="领养你的宠物",
                                         interactive=True)
            journey_rad = gr.Radio(choices=["出门旅行", "无旅行计划"], label="旅行选择", value="出门旅行",
                                   interactive=True)
            current_time_txtbox = gr.Dropdown(value=time_list[7], choices=time_list, label="选择当前时间",
                                              interactive=True)
            gpt_select_dpd = gr.Dropdown(value='gpt4', choices=['gpt3.5', 'gpt4'], label="gpt引擎选择",
                                         interactive=True, visible=False)

            pet_satiety_txtbox = gr.Textbox(lines=1, value='70', label="宠物饱腹感", interactive=True)
            pet_mood_txtbox = gr.Textbox(lines=1, value=None, label="宠物心情", interactive=True)

        with gr.Column():
            with gr.Row():
                pet_local_txtbox = gr.Textbox(lines=1, value=None, label="宠物位置", interactive=True)
                friend_pet_state_txtbox = gr.Dropdown(value=None, choices=friend_state_list,
                                                      label="朋友(合养宠物主人)状态",
                                                      interactive=True)
                pet_state_txtbox = gr.Textbox(lines=2, value=None, label="宠物当前状态", interactive=True,
                                              visible=False)
                pet_hidden_state_txtbox = gr.Textbox(lines=2, value=None, label="宠物隐藏的当前状态", interactive=True,
                                                     visible=False)
            with gr.Row():
                announcement_info_txtbox = gr.Textbox(lines=1, value=None, label="推送信息", interactive=False)

            public_screen_txtbox = gr.Textbox(lines=2, value=None, label="公告信息", max_lines=4, interactive=False)
            destination = gr.Textbox(lines=1, value=None, label="选择旅游的地方", interactive=False, visible=False)

        with gr.Row():
            pet_info_txtbox = gr.Textbox(lines=1, max_lines=4, value=get_pet_info_str(default_pet_name),
                                         label="宠物信息",
                                         interactive=False, visible=False)

        with gr.Row():
            pet_state_btn = gr.Button("刷新状态(推进1小时)")

            with gr.Column():
                stroke_type_dpd = gr.Radio(stroke_type_list, label="抚摸部位", interactive=True,
                                           value=stroke_type_list[0])

                stroke_btn = gr.Button("抚摸")

            with gr.Column():
                feed_type_dpd = gr.Radio(feed_type_list, interactive=True, value=feed_type_list[-1],
                                         label="选择投喂的食物")

                give_feed_btn = gr.Button("投喂")

    next_plan_txtbox = gr.Textbox(lines=2, value=None, label="下一步计划", visible=False)
    pet_day_plan_txtbox = gr.Textbox(lines=2, value=None, label="宠物的行程计划", interactive=True, visible=False)
    journey_img = gr.Image(type="filepath", value=None, interactive=False)

    # 重新选择宠物
    pet_select_dpd.change(select_pet, inputs=[pet_select_dpd, gpt_select_dpd],
                          outputs=[pet_info_txtbox, pet_satiety_txtbox, pet_mood_txtbox, pet_local_txtbox,
                                   announcement_info_txtbox, pet_day_plan_txtbox, pet_state_txtbox, next_plan_txtbox,
                                   current_time_txtbox, stroke_type_dpd, feed_type_dpd, public_screen_txtbox])
    # 刷新一小时
    pet_state_btn.click(get_state,
                        inputs=[current_time_txtbox, pet_satiety_txtbox, pet_hidden_state_txtbox,
                                pet_day_plan_txtbox, public_screen_txtbox, friend_pet_state_txtbox, journey_rad,
                                destination],
                        outputs=[pet_satiety_txtbox, pet_mood_txtbox, pet_local_txtbox, pet_state_txtbox,
                                 next_plan_txtbox, announcement_info_txtbox, pet_day_plan_txtbox,
                                 current_time_txtbox, public_screen_txtbox, pet_hidden_state_txtbox,
                                 friend_pet_state_txtbox, journey_img, destination])

    # 投喂
    give_feed_btn.click(give_feed,
                        inputs=[current_time_txtbox, pet_hidden_state_txtbox, feed_type_dpd, public_screen_txtbox],
                        outputs=[pet_satiety_txtbox, pet_mood_txtbox, pet_state_txtbox,
                                 pet_local_txtbox, next_plan_txtbox, public_screen_txtbox, pet_hidden_state_txtbox])

    # 主人抚摸
    stroke_btn.click(stroke_pet,
                     inputs=[current_time_txtbox, pet_state_txtbox, stroke_type_dpd, pet_satiety_txtbox,
                             public_screen_txtbox, pet_day_plan_txtbox],
                     outputs=[pet_state_txtbox, public_screen_txtbox, pet_mood_txtbox,
                              pet_satiety_txtbox])


demo.queue().launch(server_name="0.0.0.0", server_port=8705)
