import webuiapi

api = webuiapi.WebUIApi(host='202.168.100.176', port=17324)
model = "hellocartoonfilm_V13.safetensors [3ae7884eba]"
api.util_set_model(model)


def get_journey_img(prompt: str, save_img_p: str):
    lora = ' <lora:pet-000006:1>'
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

    image = api.txt2img(**sd_key_args, ).images[0]
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

    prompt = "A cute cartoon cat Egyptian pyramids"
    sp = '1.png'
    get_journey_img(prompt, sp)
