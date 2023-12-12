import os
from tqdm import tqdm
from joblib import Parallel, delayed
import config
from pathlib import Path
from general_functions import get_gpt_result, parse_res_text


def gen_new_state(pet, jour_coun, jour_place, state, api_key):
    # --------------------------------------
    # 根据已有信息，生成新的旅游内容
    # --------------------------------------
    prompt = config.replace_state_prompt.format_map(
        {'pet': pet, 'jour_place': jour_place, 'jour_coun': jour_coun, 'state': state,
         })
    # print("-" * 100)
    # print(f"journey_plan_gen prompt:\n{prompt}")
    # print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(engine_name='gpt-4', message_list=message_list, api_key=api_key)


def save_gen_new_state(pts):
    # --------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # save_path:生成的状态和图片prompt的存储路径，country jour_place：国家和地区, api_key：openai的key
    # 将生成的内容保存到对应国家和地区的文档里
    # --------------------------------------
    save_path, pet, jour_coun, jour_place, state, api_key = pts

    file_path = os.path.join(save_path, "new_description.txt")
    if not os.path.exists(file_path):

        try:
            new_state = gen_new_state(pet, jour_coun, jour_place, state, api_key)

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            with open(file_path, "w") as f:
                f.write(new_state)
        except Exception as e:
            print(e, f"error new file:{file_path}")


if __name__ == '__main__':

    countries = config.journey_places
    # 原prompt总路径
    img_dir = '/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/journey_imgs2jpg'
    # 新路径
    gen_save_dir = '/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/journey_imgs2jpg'

    api_key = [
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
        "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",
    ]

    # 从文件路径读取所有需要的相关参数，状态描述，并得到新的生成路径生成以及添加api key
    pts_cl = []
    key_num = len(api_key)
    k_n = 0
    print("读取description.txt文件中...")
    for file in tqdm([str(f) for f in Path(img_dir).rglob("description.txt")]):
        if not Path(file).parent.joinpath("new_description.txt").exists():
            with open(file, 'r') as f:
                state = f.readline()
            splits = file.split('/')
            pet, coun, place = splits[-5], splits[-4], splits[-3]
            save_path = os.path.join(gen_save_dir, pet, coun, place, splits[-2])
            pts_cl.append((save_path, pet, coun, place, state, api_key[k_n]))
            k_n += 1
            k_n = k_n % key_num

    print("进行中...")
    results = Parallel(n_jobs=key_num, backend="multiprocessing")(
        delayed(save_gen_new_state)(pts) for pts in tqdm(pts_cl))

    for _ in results:
        pass
