import os
from tqdm import tqdm
from joblib import Parallel, delayed
import re
import config
from aipet import PersonPet
from multi_api_img_service import get_journey_img
import multi_api_img_service


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


def gen_image(pts):
    save_dir, countries, pet_picture_keyword, key_value, api_key = pts
    all_pet_names = list(config.pets_dic.keys())
    default_pet_name = all_pet_names[0]
    glob_pet_obj: PersonPet = PersonPet(default_pet_name, gpt_version="gpt4", api_key=api_key)
    num_places = 20
    save_dir = save_dir
    batch_size = 4
    countries = countries
    pet_picture_keyword = pet_picture_keyword
    pet_picture_key = key_value
    for country in countries:  # config.journey_places
        place_arrived = ' '
        file_cou_dir = os.path.join(save_dir, f"{country}")
        if os.path.exists(file_cou_dir):
            pass
        else:
            os.mkdir(file_cou_dir)
        arrived_path = os.path.join(file_cou_dir, "place_arrived.txt")
        with open(arrived_path, 'w') as f:
            f.write(place_arrived + '\n')
        for _ in range(num_places):
            res_text = glob_pet_obj.journey_plan_gen(sample_destination=country, place_arrived=place_arrived)
            jour_place = parse_res_text(res_text, "景点")
            mor_jour = parse_res_text(res_text, "早上的旅行内容")
            aft_jour = parse_res_text(res_text, "下午的旅行内容")
            eve_jour = parse_res_text(res_text, "晚上的旅行内容")
            jour_place = jour_place.strip('"')
            attr_path = os.path.join(file_cou_dir, f"{jour_place}")
            jour_dic = {'morning': mor_jour,
                        'afternoon': aft_jour,
                        'evening': eve_jour, }
            place_arrived = place_arrived + "、" + jour_place
            if os.path.exists(attr_path):
                pass
            else:
                os.mkdir(attr_path)

            for jour in ['morning', 'afternoon', 'evening']:
                jour_prompt = jour_dic[jour]
                jour_prompt_eng = glob_pet_obj.get_image_prompt(prompt=f'现在是{jour}。' + jour_prompt.strip('"'),
                                                                pet_keyword=pet_picture_keyword)

                img_save_path = os.path.join(attr_path, f"{jour}")
                if os.path.exists(img_save_path):
                    pass
                else:
                    os.mkdir(img_save_path)
                text_path = os.path.join(img_save_path, "discription.txt")
                en_text_path = os.path.join(img_save_path, "en_discription.txt")
                with open(text_path, 'a') as f:
                    f.write(jour_prompt.strip('"') + '\n')
                with open(en_text_path, 'a') as f:
                    f.write(jour_prompt_eng.strip('"') + '\n')
                get_journey_img(prompt=jour_prompt_eng.strip('"'), save_img_p=img_save_path,
                                pet_keyword=pet_picture_keyword, key_value=pet_picture_key, batch_size=batch_size)
        with open(os.path.join(save_dir, f"{country}",'places.txt', 'w')) as f:
            f.write(place_arrived)
    return 1


countries = config.journey_places
pets = list(multi_api_img_service.pet_lora_dic.keys())
key_value = 0.6
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
save_dir = ["/data/Agents/img_gen/imgs/save_bear",
            "/data/Agents/img_gen/imgs/save_berrycat",
            "/data/Agents/img_gen/imgs/save_pumpkincat",
            "/data/Agents/img_gen/imgs/save_rabbit",
            "/data/Agents/img_gen/imgs/save_unicon", ]
k_n = 0
pts_cl = []
# save_dir, countries, pet_picture_keyword, key_value, api_key
for i in range(len(pets)):
    pts_cl.append((save_dir[i], countries, pets[i], key_value, api_key[k_n]))
    k_n += 1
    k_n = k_n % 15

results = Parallel(n_jobs=15, backend="multiprocessing")(delayed(gen_image)(pts) for pts in tqdm(pts_cl))
for _ in results:
    pass

