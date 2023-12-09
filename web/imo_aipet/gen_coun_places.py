import os
from tqdm import tqdm
from joblib import Parallel, delayed
import re
import config
from openai import OpenAI

def get_gpt_result(engine_name: str = 'gpt-4', message_list: list = [], api_key='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') -> str:
    api_key = api_key
    client = OpenAI(api_key=api_key, organization='org-vZinLD7D6tNWUWeWJJtAUyzD')

    response = client.chat.completions.create(
        model='gpt-4',
        messages=message_list
    )

    res_text = response.choices[0].message.content
    print("=" * 100)
    print(f"response_text:\n{res_text}")
    print("=" * 100 + "\n\n")
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
    #--------------------------------------
    # 生成某个国家：country 指定数量：num_places 个景点
    # 返回一个景点列表
    #--------------------------------------
    prompt = config.get_jour_attr.format_map(
            {'jour_coun': country,
             'num_places': num_places,
             })
    message_list = [{"role": "user", "content": prompt}]
    places = get_gpt_result(message_list=message_list, api_key=api_key)
    places = [place.strip(' ').strip("'").strip('.') for place in places.split(',')]
    return places

def gen_save_places(pts):
    #--------------------------------------
    # 生成某个国家：country 指定数量：num_places 个景点 并存到 save_dir 中
    #--------------------------------------
    save_dir, country, api_key, num_places= pts
    prompt = config.get_jour_attr.format_map(
            {'jour_coun': country,
             'num_places': num_places,
             })
    message_list = [{"role": "user", "content": prompt}]
    places = get_gpt_result(message_list=message_list, api_key=api_key)

    places_save_path = os.path.join(save_dir, f"{country}.txt")
    with open(places_save_path, "a") as f:
        f.write(places)
    return places


if __name__ == '__main__':
    countries = config.journey_places
    api_key = ["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",
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
    "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",
    "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",]

    # ---------------------------------------------
    # 获取所有国家20个景点
    # ---------------------------------------------
    k_n = 0
    pts_cl = []
    save_dir = '/data/Agents/gen_img_new/save/country_places'
    for i in range(len(countries)):
        pts_cl.append((save_dir, countries[i], api_key[k_n], 20))
        k_n += 1
        k_n = k_n % 15
    results = Parallel(n_jobs=16, backend="multiprocessing")(delayed(gen_save_places)(pts) for pts in tqdm(pts_cl))
    