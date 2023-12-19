import os
from tqdm import tqdm
from joblib import Parallel, delayed
import config
import json
from general_functions import get_gpt_result, parse_res_text
import sys


def journey_plan_gen(jour_coun, jour_place):
    # --------------------------------------
    # 生成旅游内容（早中晚中文prompt）
    # --------------------------------------
    prompt = config.journey_plan_gen_prompt.format_map(
        {'jour_place': jour_place, 'jour_coun': jour_coun,
         })
    # print("-" * 100)
    # print(f"journey_plan_gen prompt:\n{prompt}")
    # print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(message_list=message_list)


def get_image_prompt(prompt: str, coun: str, jour: str):
    # --------------------------------------
    # 生成旅游内容（早中晚英文prompt）
    # --------------------------------------
    prompt = config.img_prompt.format_map(
        {'jour_disc': prompt, 'coun': coun, 'jour': jour}, )
    # print("-" * 100)
    # print(f"get_image_prompt:\n{prompt}")
    # print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(message_list=message_list)


def gen_image_prompt(pts):
    # --------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # pts里包含：save_dir: 存图片的位置（大类，告诉是对应宠物就行），country jour_place：国家和地区
    # pet_picture_keyword
    # --------------------------------------
    country, jour_place = pts

    res_text = journey_plan_gen(jour_coun=country, jour_place=jour_place)
    mor_jour = parse_res_text(res_text, "早上的旅行内容")
    aft_jour = parse_res_text(res_text, "下午的旅行内容")
    eve_jour = parse_res_text(res_text, "晚上的旅行内容")

    jour_dic = {'morning': mor_jour,
                'afternoon': aft_jour,
                'evening': eve_jour, }

    gen_dict = {}

    for jour in ['morning', 'afternoon', 'evening']:
        jour_prompt = jour_dic[jour].strip('"')
        jour_prompt_eng = get_image_prompt(prompt=f'现在是{jour}。' + jour_prompt.strip('"'),
                                           coun=country, jour=jour_place)

        # 第一个值：中文的文案， 第二个：生成图片的英文prompt
        gen_dict[jour] = (jour_prompt.strip('"'), jour_prompt_eng.strip('"'))

    return gen_dict


def save_gen_img_prompt(pts):
    # --------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # save_dir:生成的状态和图片prompt的存储路径，country jour_place：国家和地区,
    # 将生成的内容保存到对应国家和地区的文档里
    # --------------------------------------
    """
    save_dir, country, jour_place = pts
    pts = country, jour_place
    gen_dict = gen_image_prompt(pts)"""

    save_dir, country, jour_place = pts
    file_path = os.path.join(save_dir, "gen_dict.json")
    if not os.path.exists(file_path):
        pts = country, jour_place
        gen_dict = gen_image_prompt(pts)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open(file_path, "w") as f:
            json.dump(gen_dict, f)


if __name__ == '__main__':

    countries = config.journey_places

    places_save_dir = sys.argv[1]
    gen_save_dir = sys.argv[2]

    # 将所有国家和地区景点组成一个pair
    con_place_pair = []
    for name in os.listdir(places_save_dir):
        file = os.path.join(places_save_dir, name)
        for con in countries:
            if con in file:
                with open(file, 'r') as f:
                    places = f.readline()
                con_places = [place.strip(' ').strip("'").strip('.') for place in places.split(',')]
                for place in con_places:
                    con_place_pair.append((con, place))

    pts_cl = []
    for i in range(len(con_place_pair)):
        con, jour_place = con_place_pair[i]
        # prompt生成路径
        jour_save_dir = os.path.join(gen_save_dir, con, jour_place)
        # 判断是否已经存在生成过的prompt，并将没生成过的加入生成列队
        if not os.path.exists(os.path.join(jour_save_dir, "gen_dict.json")):
            pts_cl.append((jour_save_dir, con, jour_place))

    print(f"待生成景点prompt个数:{len(pts_cl)}")
    results = Parallel(n_jobs=3, backend="multiprocessing")(delayed(save_gen_img_prompt)(pts) for pts in tqdm(pts_cl))
    for _ in results:
        pass
