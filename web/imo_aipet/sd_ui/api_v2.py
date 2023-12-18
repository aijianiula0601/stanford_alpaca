# ------------------------------------------------------------------
# 方案2
# 借助分区Prompt和局部mask提升效果
#
# 注意：方案2的prompt需要重新设计，prompt里面不要描述宠物的行为，只需要描述场景
# 比如原本的prompt为
# As the night falls, Whiskers, a cartoon rabbit, finds itself in Kabukicho, illuminated by a myriad of neon lights. The streets are ablaze with dazzling lights, bustling with crowds, and the rhythmic sounds of dance and song emanate from the nightclubs, creating a vibrant and lively atmosphere.
# 这个prompt里面描述了宠物，背景里面不要有人，应该改成如下的这种形式
# As the night falls, illuminated by a myriad of neon lights. The streets are ablaze with dazzling lights,  creating a vibrant and lively atmosphere.
#
# 场景prompt不要过于复杂，并且不要包含人，模型对人的生成不好
#
# 该方案需要输入的参数包括场景的prompt，以及宠物生成的位置，可选项为left和right
# ------------------------------------------------------------------
import requests
from util import decode_image, encode_image, image_grid

url = "http://202.168.100.176:17602"
option_payload = {
    "sd_model_checkpoint": "hellocartoonfilm_V13.safetensors [3ae7884eba]",
}

requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)


def get_single_pets_img(scene_prompt, pet_name, location, lora_model, lora_weight=1.0, steps=30, batch_size=4):
    common_prompt = 'masterpiece, best quality, no person'
    pets_prompt = f'a cartoon {pet_name}'

    param_mapping = {'left': {'prompt': f'{common_prompt} ADDCOMM\n{scene_prompt} ADDROW\n{pets_prompt} ADDCOL',
                              'Regional_matrix': "1,1;1,1,1", 'lora_mask': encode_image('assert/left_bottom.png')},
                     'right': {'prompt': f'{common_prompt} ADDCOMM\n{scene_prompt} ADDROW\nADDCOL\n{pets_prompt}',
                               'Regional_matrix': "1,1;1,1,1", 'lora_mask': encode_image('assert/right_bottom.png')}
                     }

    param = param_mapping[location]

    payload = {
        "prompt": param['prompt'],
        "negative_prompt": "",
        "width": 900,
        "height": 900,
        "steps": steps,
        "cfg": 7,
        "sampler_index": "DPM++ 2M Karras",
        "seed": -1,
        "batch_size": batch_size,
        "enable_hr": True,
        "hr_scale": 1,
        "hr_upscaler": "None",
        "alwayson_scripts": {
            "Regional Prompter": {
                "args": [True, False, "Matrix", "Columns", "Mask", "Prompt", param['Regional_matrix'], "0.2", False,
                         True, False, "Attention"]
            },
            "LoRA models Masks for generating": {
                "args": [True, lora_model, lora_weight, "", 0, "", 0, param['lora_mask']]
            }
        }
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    res = response.json()

    generate_imgs = [decode_image(img) for img in res['images'][:batch_size]]
    return generate_imgs


if __name__ == '__main__':
    pet_name = 'rabbit'
    location_list = ['right', 'left']
    scene_prompt = 'Temple of Heaven.'
    lora_model = 'pets-rabbit-20231204-512'
    lora_weight = 1.0
    steps = 30
    batch_size = 2

    generate_imgs = get_single_pets_img(scene_prompt, pet_name, location_list[0], lora_model, lora_weight, steps,
                                        batch_size)
    img = image_grid(generate_imgs, batch_size // 2, 2)
    img.save('/Users/jiahong/Downloads/single_pets.jpg', quality=95)  # 直接用jpg保存，节省空间
