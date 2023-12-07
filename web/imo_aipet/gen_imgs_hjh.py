import random
import os
import webuiapi
from multi_api_img_service import *
from aipet import PersonPet

from tqdm import tqdm
from joblib import Parallel, delayed
import utils
import config
import multi_api_img_service


def gen_country_images(args):
    num_places, save_dir, country, pet_picture_keyword, pet_picture_key, batch_size, api_key = args
    person_pet = PersonPet(all_pet_names[0], gpt_version="gpt4", api_key=api_key)

    place_arrived = ' '
    file_cou_dir = os.path.join(save_dir, f"{country}")

    os.system(f"mkdir -p {file_cou_dir}")
    arrived_path = os.path.join(file_cou_dir, "place_arrived.txt")
    with open(arrived_path, 'a') as f:
        f.write(place_arrived + '\n')
    for _ in range(num_places):
        try:
            res_text = person_pet.journey_plan_gen(sample_destination=country, place_arrived=place_arrived)
            jour_place = utils.parse_res_text(res_text, "景点")
            mor_jour = utils.parse_res_text(res_text, "早上的旅行内容")
            aft_jour = utils.parse_res_text(res_text, "下午的旅行内容")
            eve_jour = utils.parse_res_text(res_text, "晚上的旅行内容")
            jour_place = jour_place.strip('"').replace(" ", "-")
            attr_path = os.path.join(file_cou_dir, f"{jour_place}")
            jour_dic = {'morning': mor_jour,
                        'afternoon': aft_jour,
                        'evening': eve_jour, }
            place_arrived = place_arrived + "、" + jour_place
            os.system(f"mkdir -p {attr_path}")
            for jour in ['morning', 'afternoon', 'evening']:
                jour_prompt = jour_dic[jour]
                jour_prompt_eng = person_pet.get_image_prompt(prompt=f'现在是{jour}。' + jour_prompt.strip('"'),
                                                              pet_keyword=pet_picture_keyword)

                img_save_dir = os.path.join(attr_path, f"{jour}")
                os.system(f"mkdir -p {img_save_dir}")
                assert os.path.exists(img_save_dir), f"file not directory not exist: {img_save_dir}"

                text_path = os.path.join(img_save_dir, "description.txt")
                en_text_path = os.path.join(img_save_dir, "en_description.txt")

                with open(text_path, 'a') as f:
                    f.write(jour_prompt.strip('"') + '\n')
                with open(en_text_path, 'a') as f:
                    f.write(jour_prompt_eng.strip('"') + '\n')

                get_journey_img(prompt=jour_prompt_eng.strip('"'), save_img_p=img_save_dir,
                                pet_keyword=pet_picture_keyword, key_value=pet_picture_key, batch_size=batch_size)
                print(f"-----country:{country}, 景点:{jour_place} done!")
        except Exception as e:
            print(e)
            pass

    with open(os.path.join(save_dir, f"{country}", 'places.txt', 'w')) as f:
        f.write(place_arrived)

    return 1


countries = config.journey_places
pets = list(multi_api_img_service.pet_lora_dic.keys())
key_value = 0.6
num_places = 20
batch_size = 4

pts_cl = []
for i in range(len(pets)):
    save_dir = utils.save_dir[i]
    all_pet_names = list(config.pets_dic.keys())
    pet_picture_keyword = pets[i]
    api_key = random.sample(utils.api_key_list, k=1)[0]
    for country in countries:
        pts_cl.append((num_places, save_dir, country, pet_picture_keyword, key_value, batch_size, api_key))

results = Parallel(n_jobs=15, backend="multiprocessing")(delayed(gen_country_images)(pts) for pts in tqdm(pts_cl))
for _ in results:
    pass
