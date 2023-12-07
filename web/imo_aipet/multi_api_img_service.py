import random
import webuiapi


# -------------------------------------------------
# 初始化服务
# -------------------------------------------------

def init_models(host, port):
    api = webuiapi.WebUIApi(host=host, port=port)
    model = 'hellocartoonfilm_V13.safetensors [3ae7884eba]'
    api.util_set_model(model)
    return api

"""
ip_port_list = [
    ('202.168.100.176', 17601),
    ('202.168.100.176', 17602),
    ('202.168.100.176', 17603),
    ('202.168.100.176', 17604),
    ('202.168.100.176', 17605),
    ('202.168.100.176', 17606),
    ('202.168.100.176', 17607),
]"""

ip_port_list = [
    ('202.168.100.178', 2004),
    ('202.168.100.178', 2005),
    ('202.168.100.178', 2006),
    ('202.168.100.178', 2007),
    ('202.168.100.178', 2008),
    ('202.168.100.178', 2009),
    ('202.168.100.178', 2010),
    ('202.168.100.178', 2011),
    ('202.168.100.178', 2000),
    ('202.168.100.178', 2001),
    ('202.168.100.178', 2002),
    ('202.168.100.178', 2003),
    ('202.168.100.178', 2012),
    ('202.168.100.178', 2013),
    ('202.168.100.178', 2014),
    ('202.168.100.178', 2015),
]

inited_api_list = [init_models(t[0], t[1]) for t in ip_port_list]

# -------------------------------------------------
# -------------------------------------------------

pet_lora_dic = {
    "a cartoon bear": "<lora:pets-bear-20231204:",
    "a cartoon blueberry_cat": "<lora:pets-blueberry_cat-20231204:",
    "a cartoon pumpkin_cat": "<lora:pets-pumpkin_cat-20231204:",
    "a cartoon rabbit": "<lora:pets-rabbit-20231204:",
    "a cartoon unicon": "<lora:pets-unicon-20231204:",
}


def get_journey_img(prompt: str, save_img_p: str, pet_keyword: str, key_value=1, batch_size=0.6):
    prompt += pet_lora_dic[pet_keyword] + str(key_value) + '>'
    print(batch_size)

    sd_key_args = {
        "height": 512,
        "width": 512,
        "steps": 40,
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
    """
    sd_key_args = {
        "height": 512,
        "width": 512,
        "steps": 40,
        "cfg_scale": 7.0,
        "sampler_name": "DPM++ 2M Karras",
        "restore_faces": False,
        "prompt": prompt,
        "seed": -1,
        "batch_size":batch_size
    }"""

    image = random.sample(inited_api_list, k=1)[0].txt2img(**sd_key_args, ).images
    # print(ima)
    print(image)
    if batch_size == 1:
        image[0].save(save_img_p)
    else:
        for i in range(batch_size):
            image[i].save(save_img_p + f'/{i}.png')
    # image.save(save_img_p)
    print(f"save img to:{save_img_p}")
    return image


if __name__ == '__main__':
    # -----------------------------
    # 说明：
    # 1.prompt用英文描述效果最佳，最好用英文
    # 2.如果是猫：prompt中加入 "A cute cartoon cat" 采用有猫在图片中，如果生成的图片有猫在图片，加入这个prompt
    # 3.如果是兔子：prompt中加入 "a small bunny toy" 采用有兔子在图片中，如果生成的图片有猫在图片，加入这个prompt
    # -----------------------------

    prompt = "As the night falls, Whiskers, a cartoon blueberry_cat, finds itself in Kabukicho, illuminated by a myriad of neon lights. The streets are ablaze with dazzling lights, bustling with crowds, and the rhythmic sounds of dance and song emanate from the nightclubs, creating a vibrant and lively atmosphere."
    sp = './'
    get_journey_img(prompt, sp, pet_keyword="a cartoon blueberry_cat", key_value=1, batch_size=3)
