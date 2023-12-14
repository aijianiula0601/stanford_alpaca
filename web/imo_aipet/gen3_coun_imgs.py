import os
from tqdm import tqdm
from joblib import Parallel, delayed
import webuiapi
import config
import json
import math
import random
import time

from general_functions import replace_character_prompt


# -------------------------------------------------
# 初始化服务
# -------------------------------------------------

def init_models(host, port):
    api = webuiapi.WebUIApi(host=host, port=port)
    model = 'hellocartoonfilm_V13.safetensors [3ae7884eba]'
    api.util_set_model(model)
    return api


ip_port_list = [
    # ('202.168.100.176', 17601),
    ('202.168.100.176', 17602),
    ('202.168.100.176', 17603),
    ('202.168.100.176', 17604),
    ('202.168.100.176', 17605),
    ('202.168.100.176', 17606),
    ('202.168.100.178', 2000),
    ('202.168.100.178', 2001),
    ('202.168.100.178', 2002),
    ('202.168.100.178', 2003),
    ('202.168.100.178', 2004),
    ('202.168.100.178', 2005),
    ('202.168.100.178', 2006),
    ('202.168.100.178', 2007),
    ('202.168.100.178', 2008),
    ('202.168.100.178', 2009),
    ('202.168.100.178', 2010),
    ('202.168.100.178', 2011),
    ('202.168.100.178', 2012),
    ('202.168.100.178', 2013),
    ('202.168.100.178', 2014),
    ('202.168.100.178', 2015),
]

inited_api_list = [init_models(t[0], t[1]) for t in ip_port_list]

# 宠物对应的lora
pet_lora_dic = {
    "bear": "<lora:pets-bear-20231204-512:0.6>",
    "blueberry_cat": "<lora:pets-blueberry_cat-20231204-512:0.6>",
    "pumpkin_cat": "<lora:pets-pumpkin_cat-20231204-512:0.6>",
    "rabbit": "<lora:pets-rabbit-20231204-512:0.6>",
    "unicorn": "<lora:pets-unicorn-20231207-512:1>",
}

# 宠物对应的关键词
pet_lora_key_word = {
    "bear": "a cartoon bear",
    "blueberry_cat": "a cartoon blueberry_cat",
    "pumpkin_cat": "a cartoon pumpkin_cat",
    "rabbit": "a cartoon rabbit lora",
    "unicorn": "A cartoon unicorn",
}


def get_journey_img(prompt: str, pic_description: str, save_img_dir: str, pet_keyword: str, api: webuiapi.WebUIApi,
                    batch_size=1):
    prompt += pet_lora_dic[pet_keyword]
    # 目录已经存在的话，不用生成
    if not os.path.exists(save_img_dir):
        sd_key_args = {
            "height": 512,
            "width": 512,
            "steps": 20,
            "enable_hr": True,
            "denoising_strength": 0.2,
            "hr_upscaler": "R-ESRGAN 4x+",
            "hr_resize_x": 900,
            "hr_resize_y": 900,
            "cfg_scale": 7.0,
            "sampler_name": "DPM++ 2M Karras",
            "restore_faces": False,
            "prompt": prompt,
            "seed": -1,
            "batch_size": batch_size
        }
        image = api.txt2img(**sd_key_args, ).images
        for i in range(batch_size):
            if not os.path.exists(save_img_dir):
                os.makedirs(save_img_dir)
            img_p = f"{save_img_dir}/{i}.png"
            image[i].save(img_p)

        with open(os.path.join(save_img_dir, "description.txt"), "w") as f:
            f.write(pic_description.strip('"'))
        with open(os.path.join(save_img_dir, "prompt.txt"), "w") as f:
            f.write(prompt.strip('"'))


def jour_img_gen(pts: list):
    api, pts_list = pts
    for pt in tqdm(pts_list):
        jour_save_dir, pet_name, prompt, pic_description, batch_size = pt
        get_journey_img(prompt=prompt, pic_description=pic_description, save_img_dir=jour_save_dir,
                        pet_keyword=pet_name, api=api,
                        batch_size=batch_size)


if __name__ == '__main__':
    bath_size = 4
    n_job = len(ip_port_list)
    countries = config.journey_places

    base_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet"
    # 已经生成了prompt和文字的保存目录
    description_prompt_dir = f'{base_dir}/gen_prompts'
    # 生成图片的保存目录
    img_save_dir = f'{base_dir}/journey_imgs'

    # 保存此次生成的日记
    log_text_file = f"{base_dir}/journey_imgs_log.txt"
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
        for place in os.listdir(os.path.join(description_prompt_dir, coun)):
            with open(os.path.join(description_prompt_dir, coun, place, 'gen_dict.json'), 'r') as f:
                gen_dict = json.load(f)
                # 国家、景点、gen_dic
                prompt_qua.append((coun, place, gen_dict))

    # ----------------------------
    # 获取多进程的参数
    # ----------------------------
    pts_cl = []
    for con, jour_place, gen_dict in prompt_qua:
        for pet_name in pet_lora_dic.keys():
            for ti in gen_dict.keys():
                time_save_dir = f"{img_save_dir}/{pet_name}/{con}/{jour_place}/{ti}".replace(" ", "_")
                pic_description = gen_dict[ti][0]
                org_pic_prompt = gen_dict[ti][1]
                # 特殊关键词换为我们宠物的关键词
                pic_prompt = replace_character_prompt(org_prompt=org_pic_prompt.lower(),
                                                      pet_kw=pet_lora_key_word[pet_name])
                assert pic_prompt is not None, f"prompt replace error, dir:{time_save_dir}, prompt: {org_pic_prompt}"
                if not os.path.exists(time_save_dir) and pic_prompt is not None:
                    log_f.write(f"【{time_str}】{time_save_dir}\n")
                    pts_cl.append((time_save_dir, pet_name, pic_prompt, pic_description, bath_size))

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
