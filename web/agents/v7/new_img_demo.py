import webuiapi

api = webuiapi.WebUIApi(host='202.168.100.176', port=23006)
model = "hellocartoonfilm_V13.safetensors [3ae7884eba]"

pet_lora_dic = {
    "A cute cartoon cat": ' <lora:pet-000006:1>',  # 猫 的lora模型  关键字：A cute cartoon cat
    "a small bunny toy": " happy<lora:pet_20231123_1:1>"  # 兔子 的lora模型  关键字：a small bunny toy
}

api.util_set_model(model)


def get_journey_img(prompt: str, pet_keyword: str):
    prompt += pet_lora_dic[pet_keyword]

    sd_key_args = {
        "height": 512,
        "width": 512,
        "steps": 40,
        "cfg_scale": 7.0,
        "sampler_name": "DPM++ 2M Karras",
        "restore_faces": False,
        "prompt": prompt,
        "seed": -1,
        "batch_size": 2

    }

    image_list = api.txt2img(**sd_key_args, ).images

    for i, image in enumerate(image_list):
        print(image)
        save_img_p = f"1_{i}.png"
        image.save(save_img_p)
        print(f"save img to:{save_img_p}")


if __name__ == '__main__':
    # -----------------------------
    # 说明：
    # 1.prompt用英文描述效果最佳，最好用英文
    # 2.如果是猫：prompt中加入 "A cute cartoon cat" 采用有猫在图片中，如果生成的图片有猫在图片，加入这个prompt
    # 3.如果是兔子：prompt中加入 "a small bunny toy" 采用有兔子在图片中，如果生成的图片有猫在图片，加入这个prompt
    # -----------------------------

    prompt = 'a small bunny toy, (the background is the Egyptian pyramids:1.2)'
    get_journey_img(prompt, pet_keyword="a small bunny toy")
