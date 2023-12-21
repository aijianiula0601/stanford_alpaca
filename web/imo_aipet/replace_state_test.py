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
    desc = "夜幕下的加尔各答灯火辉煌，街边小吃的香气四溢，人群熙熙攘攘。"

    res = gen_new_state_my(pet="pumpkin_cat", jour_place="加尔各答风景区", jour_coun="印度", state=desc)

    print(res)

    en_res = gen_new_state_en(res)

    print(en_res)
