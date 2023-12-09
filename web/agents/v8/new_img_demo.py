import webuiapi
import random


def init_models(host, port):
    api = webuiapi.WebUIApi(host=host, port=port)
    model = 'hellocartoonfilm_V13.safetensors [3ae7884eba]'
    api.util_set_model(model)
    return api


ip_port_list = [
    ('202.168.100.176', 17601),
    ('202.168.100.176', 17602),
    ('202.168.100.176', 17603),
    ('202.168.100.176', 17604),
    ('202.168.100.176', 17605),
    ('202.168.100.176', 17606),
    ('202.168.100.176', 17607),
]
inited_api_list = [init_models(t[0], t[1]) for t in ip_port_list]


def get_journey_img(prompt: str, save_img_p: str):
    lora = ' <lora:pets-rabbit-20231204:0.6>'
    prompt += lora

    sd_key_args = {
        "height": 512,
        "width": 512,
        "steps": 40,
        "cfg_scale": 7.0,
        "sampler_name": "DPM++ 2M Karras",
        "restore_faces": False,
        "prompt": prompt,
        "seed": -1
    }

    image = random.sample(inited_api_list, k=1)[0].txt2img(**sd_key_args, ).images[0]
    print(image)
    image.save(save_img_p)
    print(f"save img to:{save_img_p}")
    return image


if __name__ == '__main__':
    # -----------------------------
    # 说明：
    # 1.prompt用英文描述效果最佳，最好用英文
    # 2.prompt中加入 "A cute cartoon cat "采用有猫在图片中，如果生成的图片有猫在图片，加入这个prompt
    # -----------------------------

    prompt = "As the night falls, Whiskers, a cartoon rabbit, finds itself in Kabukicho, illuminated by a myriad of neon lights. The streets are ablaze with dazzling lights, bustling with crowds, and the rhythmic sounds of dance and song emanate from the nightclubs, creating a vibrant and lively atmosphere. "
    sp = '1.png'
    get_journey_img(prompt, sp)
