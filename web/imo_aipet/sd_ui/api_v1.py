# ---------------------------------------------------
# 方案1
# prompt中描述场景和宠物，直接调用模型
# 这种方式badcase比较多，景点容易出不来，prompt比较复杂时，宠物生成也会有问题
# ---------------------------------------------------

import webuiapi

api = webuiapi.WebUIApi(host='202.168.100.176', port=17600)
model = "hellocartoonfilm_V13.safetensors [3ae7884eba]"
api.util_set_model(model)

prompt = 'a cat in city street'
lora = ' <lora:xxx:1>'
prompt += lora
batch_size = 2

sd_key_args = {
    "height": 512,
    "width": 512,
    "steps": 30,
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

image = api.txt2img(**sd_key_args, ).images[0]
image.save('1.png')
