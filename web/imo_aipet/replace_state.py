import os
from tqdm import tqdm
from joblib import Parallel, delayed
import config
from pathlib import Path
import openai
import random

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"


def get_gpt_result(message_list):
    """
    微软的openai账号
    """
    response = openai.ChatCompletion.create(
        engine='gpt-35-turbo',
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content'].strip('"').strip('“').strip('”')


def gen_new_state(pet, jour_coun, jour_place, state):
    # --------------------------------------
    # 根据已有信息，生成新的旅游内容
    # --------------------------------------

    replace_state_prompt_list = [config.replace_state_prompt1, config.replace_state_prompt2]

    prompt = random.sample(replace_state_prompt_list, k=1)[0].format_map(
        {'pet': pet, 'jour_place': jour_place, 'jour_coun': jour_coun, 'state': state,
         })
    # print("-" * 100)
    # print(f"journey_plan_gen prompt:\n{prompt}")
    # print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(message_list)


def save_gen_new_state(pts):
    # --------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # save_path:生成的状态和图片prompt的存储路径，country jour_place：国家和地区, api_key：openai的key
    # 将生成的内容保存到对应国家和地区的文档里
    # --------------------------------------
    save_dir, pet, jour_coun, jour_place, state = pts

    file_path = os.path.join(save_dir, "new_description.txt")
    if not os.path.exists(file_path):

        try:
            new_state = gen_new_state(pet, jour_coun, jour_place, state)

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            with open(file_path, "w") as f:
                f.write(new_state)
        except Exception as e:
            print(e, f"error new file:{file_path}")


if __name__ == '__main__':
    countries = config.journey_places

    base_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/region/20231219"
    # 原prompt总路径
    img_dir = f'{base_dir}/journey_imgs'
    # 新路径
    gen_save_dir = img_dir

    # 从文件路径读取所有需要的相关参数，状态描述，并得到新的生成路径生成以及添加api key
    pts_cl = []
    print("读取description.txt文件中...")
    for org_f in Path(img_dir).rglob("description.txt"):
        file = str(org_f)
        if not Path(file).parent.joinpath("new_description.txt").exists():
            with open(file, 'r') as f:
                state = f.readline()
            splits = file.split('/')
            pet, coun, place = splits[-5], splits[-4], splits[-3]
            save_dir = os.path.join(gen_save_dir, pet, coun, place, splits[-2])
            pts_cl.append((save_dir, pet, coun, place, state))

    print("进行中...")
    results = Parallel(n_jobs=20, backend="multiprocessing")(
        delayed(save_gen_new_state)(pts) for pts in tqdm(pts_cl))

    for _ in results:
        pass
