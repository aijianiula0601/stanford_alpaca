from replace_state import *


def gen_new_state_my(pet, jour_coun, jour_place, state):
    # --------------------------------------
    # 根据已有信息，生成新的旅游内容
    # --------------------------------------

    replace_state_prompt_list = [config.replace_state_prompt1]

    prompt = random.sample(replace_state_prompt_list, k=1)[0].format_map(
        {'pet': pet, 'jour_place': jour_place, 'jour_coun': jour_coun, 'state': state,
         })
    # print("-" * 100)
    # print(f"journey_plan_gen prompt:\n{prompt}")
    # print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    return get_gpt_result(message_list)


if __name__ == '__main__':
    desc = "早晨的阳光洒在楚格峰上，我在清新的空气中嬉戏，欣赏着远处连绵的阿尔卑斯山脉。"

    res = gen_new_state_my(pet="pumpkin_cat", jour_coun="瑞士", jour_place="楚格峰", state=desc)

    print(res)

    en_res = gen_new_state_en(res)

    print(en_res)
