import os
from tqdm import tqdm
from joblib import Parallel, delayed
import re
import config
import openai

openai.api_type = "azure"
openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'


def get_gpt_result(message_list: list) -> str:
    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    res_text = response.choices[0].message.content
    return res_text


def parse_res_text(res_text: str, key: str):
    pattern = r'"{0}"\s*:\s*("[^"]*"|[^",]*)'.format(key)
    # pattern = r'"{0}"：\s*"([^"]*)"'.format(key)

    match = re.search(pattern, res_text)
    if match:
        value = match.group(1)
        return value
    else:
        pattern = r'"{0}"\s*：\s*("[^"]*"|[^",]*)'.format(key)
        match = re.search(pattern, res_text)
        if match:
            value = match.group(1)
            return value
        else:
            return None


def gen_places(country, api_key, num_places=20):
    # --------------------------------------
    # 生成某个国家：country 指定数量：num_places 个景点
    # 返回一个景点列表
    # --------------------------------------
    prompt = config.get_jour_attr.format_map(
        {'jour_coun': country,
         'num_places': num_places,
         })
    message_list = [{"role": "user", "content": prompt}]
    places = get_gpt_result(message_list=message_list, api_key=api_key)
    places = [place.strip(' ').strip("'").strip('.') for place in places.split(',')]
    return places


def gen_save_places(pts):
    # --------------------------------------
    # 生成某个国家：country 指定数量：num_places 个景点 并存到 save_dir 中
    # --------------------------------------
    save_dir, country, num_places, places_save_path = pts
    prompt = config.get_jour_attr.format_map(
        {'jour_coun': country,
         'num_places': num_places,
         })
    message_list = [{"role": "user", "content": prompt}]
    places = get_gpt_result(message_list=message_list)
    with open(places_save_path, "w") as f:
        f.write(places)


if __name__ == '__main__':
    countries = config.journey_places

    # ---------------------------------------------
    # 获取所有国家20个景点
    # ---------------------------------------------
    pts_cl = []
    places_num = 20
    save_dir = '/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/country_places'
    for i in range(len(countries)):
        places_save_path = os.path.join(save_dir, f"{countries[i]}.txt")
        if not os.path.exists(places_save_path):
            pts_cl.append((save_dir, countries[i], places_num, places_save_path))
    results = Parallel(n_jobs=5, backend="multiprocessing")(delayed(gen_save_places)(pts) for pts in tqdm(pts_cl))
    for _ in results:
        pass
