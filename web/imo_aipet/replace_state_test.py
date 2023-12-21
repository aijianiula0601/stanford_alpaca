from replace_state import *

if __name__ == '__main__':
    desc = "晨光中，我在冰川湖边漫步，湖水反射着柔和的光芒，冰块轻轻漂浮。"

    res = gen_new_state(pet="pumpkin_cat", jour_place="冰川湖", jour_coun="冰岛", state=desc)

    print(res)

    en_res = gen_new_state_en(res)

    print(en_res)
