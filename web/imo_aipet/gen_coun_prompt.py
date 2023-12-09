import os
from tqdm import tqdm
from joblib import Parallel, delayed
import config
import json
from general_functions import get_gpt_result, parse_res_text

def journey_plan_gen(jour_coun, jour_place, api_key):
    #--------------------------------------
    # 生成旅游内容（早中晚中文prompt）
    #--------------------------------------
    prompt = config.journey_plan_gen_prompt.format_map(
        {'jour_place': jour_place, 'jour_coun':jour_coun,
            })
    print("-" * 100)
    print(f"journey_plan_gen prompt:\n{prompt}")
    print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(engine_name='gpt-4', message_list=message_list, api_key=api_key)

def get_image_prompt(prompt: str, api_key):
    #--------------------------------------
    # 生成旅游内容（早中晚英文prompt）
    #--------------------------------------
    prompt = config.img_prompt.format_map(
        {'jour_disc':prompt})
    print("-" * 100)
    print(f"get_image_prompt:\n{prompt}")
    print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(engine_name='gpt-4', message_list=message_list, api_key=api_key)

def gen_image_prompt(pts):
    #--------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # pts里包含：save_dir: 存图片的位置（大类，告诉是对应宠物就行），country jour_place：国家和地区
    # pet_picture_keyword, api_key：openai的key
    #--------------------------------------
    country, jour_place, api_key = pts

    res_text = journey_plan_gen(jour_coun=country, jour_place=jour_place, api_key=api_key)
    mor_jour = parse_res_text(res_text, "早上的旅行内容")
    aft_jour = parse_res_text(res_text, "下午的旅行内容")
    eve_jour = parse_res_text(res_text, "晚上的旅行内容")
    jour_place = jour_place.strip('"')

    jour_dic = {'morning': mor_jour,
                'afternoon': aft_jour,
                'evening': eve_jour, }
    
    gen_dict = {}

    for jour in ['morning', 'afternoon', 'evening']:
        jour_prompt = jour_dic[jour].strip('"')
        jour_prompt_eng = get_image_prompt(prompt=f'现在是{jour}。' + jour_prompt.strip('"'),
                                                        api_key=api_key)

        ### 第一个值：中文的文案， 第二个：生成图片的英文prompt
        gen_dict[jour] = (jour_prompt.strip('"'), jour_prompt_eng.strip('"'))

    return gen_dict

def save_gen_img_prompt(pts):
    #--------------------------------------
    # 一体化的生成旅行内容、中英文描述的函数
    # save_path:生成的状态和图片prompt的存储路径，country jour_place：国家和地区, api_key：openai的key
    # 将生成的内容保存到对应国家和地区的文档里
    #--------------------------------------
    save_path, country, jour_place, api_key = pts
    pts = country, jour_place, api_key
    gen_dict = gen_image_prompt(pts)

    file_path = os.path.join(save_path, "gen_dict.json")
    with open(file_path, "w") as f:
        json.dump(gen_dict, f)


if __name__ == '__main__':

    countries = config.journey_places
    places_save_dir = '/data/Agents/gen_img_new/save/country_places'
    gen_save_dir = '/data/Agents/gen_img_new/save/gen_save'

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


 ## 将所有国家和地区景点组成一个pair 
    con_place_pair = []
    
    for name in os.listdir(places_save_dir):
        file = os.path.join(places_save_dir,name)
        for con in countries:
            if con in file:
                with open(file, 'r') as f:
                    places = f.readline()
                con_places = [place.strip(' ').strip("'").strip('.') for place in places.split(',')]
                for place in con_places:
                    con_place_pair.append((con, place))

    k_n = 0
    pts_cl = []

    for i in range(len(con_place_pair)):
        con, jour_place = con_place_pair[i]

        con_save_path = os.path.join(gen_save_dir, f"{con}")
        if os.path.exists(con_save_path):
            pass
        else:
            os.mkdir(con_save_path)

        jour_save_path = os.path.join(con_save_path, f"{jour_place}")
        if os.path.exists(jour_save_path):
            pass
        else:
            os.mkdir(jour_save_path)

        if not os.path.exists(os.path.join(jour_save_path, "gen_dict.json")):
            pts_cl.append((jour_save_path, con, jour_place, api_key[k_n]))
            k_n += 1
            k_n = k_n % 15

    results = Parallel(n_jobs=15, backend="multiprocessing")(delayed(save_gen_img_prompt)(pts) for pts in tqdm(pts_cl))
    