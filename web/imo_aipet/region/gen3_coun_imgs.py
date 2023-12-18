import os
import sys
from tqdm import tqdm
from joblib import Parallel, delayed
import webuiapi
import config
import json
import math
import random
import time

pdj = os.path.dirname(os.path.abspath(__file__))
print('pdj：', pdj)
sys.path.append(pdj)

from sd_ui.api_v2 import get_single_pets_img, init_api


# -------------------------------------------------
# 采用分区的方式来调用
# -------------------------------------------------

# -------------------------------------------------
# 初始化服务
# -------------------------------------------------

def init_models(host, port):
    return init_api(host, port)


ip_api_list = [
    ('202.168.100.176', 17601),
    ('202.168.100.176', 17602),
    ('202.168.100.176', 17603),
    ('202.168.100.176', 17604),
    ('202.168.100.176', 17605),
    # ('202.168.100.176', 17606),
    ('202.168.100.178', 2000),
    ('202.168.100.178', 2001),
    ('202.168.100.178', 2002),
    ('202.168.100.178', 2003),
    ('202.168.100.178', 2004),
    ('202.168.100.178', 2005),
    ('202.168.100.178', 2006),
    ('202.168.100.178', 2007),
    # ('202.168.100.178', 2008),
    # ('202.168.100.178', 2009),
    # ('202.168.100.178', 2010),
    # ('202.168.100.178', 2011),
    # ('202.168.100.178', 2012),
    # ('202.168.100.178', 2013),
    # ('202.168.100.178', 2014),
    # ('202.168.100.178', 2015),
]

inited_api_list = [init_models("http://" + t[0], t[1]) for t in ip_api_list]

# 宠物对应的lora, （宠物关键词，lora名字，lora权重）
pet_lora_dic = {
    "bear": ("pets-bear-20231204-512", 1),
    "blueberry_cat": ("pets-blueberry_cat-20231204-512", 1),
    "pumpkin_cat": ("pets-pumpkin_cat-20231204-512", 1),
    "rabbit": ("pets-rabbit-20231204-512", 1),
    "unicorn": ("pets-unicorn-20231207-512", 1),
}


def get_journey_img(scene_prompt: str, pet_name: str, pic_description: str, save_img_dir: str, url: str, batch_size=1):
    location = random.sample(['right', 'left'], k=1)[0]
    lora_model = pet_lora_dic[pet_name][0]
    lora_weight = pet_lora_dic[pet_name][1]
    steps = 20

    # 目录已经存在的话，不用生成
    if not os.path.exists(save_img_dir):
        image, payload, url = get_single_pets_img(scene_prompt,
                                                  pet_name,
                                                  location=location,
                                                  lora_model=lora_model,
                                                  url=url,
                                                  lora_weight=lora_weight,
                                                  steps=steps,
                                                  batch_size=batch_size)

        for i in range(batch_size):
            if not os.path.exists(save_img_dir):
                os.makedirs(save_img_dir)
            img_p = f"{save_img_dir}/{i}.jpg"
            image[i].save(img_p, quality=95)

        with open(os.path.join(save_img_dir, "description.txt"), "w") as f:
            f.write(pic_description.strip('"'))
        with open(os.path.join(save_img_dir, "prompt.txt"), "w") as f:
            f.write(scene_prompt.strip('"'))
        with open(os.path.join(save_img_dir, "url.txt"), "w") as f:
            f.write(url)
        payload_json_f = os.path.join(save_img_dir, "payload.json")
        json.dump(payload, open(payload_json_f, 'w'))


def jour_img_gen(pts: list):
    url, pts_list = pts
    for pt in tqdm(pts_list):
        scene_prompt, pet_name, pic_description, save_img_dir, batch_size = pt
        get_journey_img(scene_prompt, pet_name, pic_description, save_img_dir, url, batch_size)


if __name__ == '__main__':
    bath_size = 4
    n_job = len(ip_api_list)
    countries = config.journey_places_v1

    base_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/region"
    # 已经生成了prompt和文字的保存目录
    description_prompt_dir = f'{base_dir}/gen_prompts'
    # 生成图片的保存目录
    img_save_dir = f'{base_dir}/journey_imgs_20231218_region_test'

    # 保存此次生成的日记
    log_text_file = f"{img_save_dir}_log.txt"
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log_f = open(log_text_file, 'a', buffering=1)
    log_f.write("-" * 100 + "\n")
    log_f.write(f"time:{time_str}\n")
    log_f.write("-" * 100 + "\n")

    # ----------------------------
    # 获取文案、图片prompt数据列表
    # ----------------------------
    prompt_qua = []
    for coun in countries:
        coun_dir = os.path.join(description_prompt_dir, coun)
        if os.path.exists(coun_dir):
            for place in os.listdir(coun_dir):
                with open(os.path.join(description_prompt_dir, coun, place, 'gen_dict.json'), 'r') as f:
                    gen_dict = json.load(f)
                    # 国家、景点、gen_dic
                    prompt_qua.append((coun, place, gen_dict))
        else:
            print(f"directory not exist:{coun_dir}")

    # ----------------------------
    # 获取多进程的参数
    # ----------------------------
    pts_cl = []
    for con, jour_place, gen_dict in prompt_qua:
        for pet_name in pet_lora_dic.keys():
            for ti in gen_dict.keys():
                time_save_dir = f"{img_save_dir}/{pet_name}/{con}/{jour_place}/{ti}".replace(" ", "_")
                pic_description = gen_dict[ti][0]
                pic_scene_prompt = gen_dict[ti][1]
                assert pic_scene_prompt is not None, f"prompt replace error, dir:{time_save_dir}, prompt: {pic_scene_prompt}"
                if not os.path.exists(time_save_dir) and pic_scene_prompt is not None:
                    log_f.write(f"【{time_str}】{time_save_dir}\n")
                    pts_cl.append((pic_scene_prompt, pet_name, pic_description, time_save_dir, bath_size))

    random.shuffle(pts_cl)
    # ----------------------------
    # 参数分组
    # ----------------------------
    args_list = []
    num_div = math.ceil(len(pts_cl) / n_job)
    api_i = 0
    for i in range(0, len(pts_cl), num_div):
        assert api_i < len(inited_api_list), f"error api_i:{api_i}"
        args_list.append((inited_api_list[api_i], pts_cl[i:i + num_div]))
        api_i += 1

    results = Parallel(n_jobs=n_job, backend="multiprocessing")(delayed(jour_img_gen)(pts) for pts in tqdm(args_list))
    for _ in results:
        pass
