import math
from utils import get_get_dialogue_qas


def check_limit_turn_dialogue(all_dialogue_qa, limit_turn_n):
    """
    查看大于多少轮的聊天
    """

    re_dia_list = []

    for dia in all_dialogue_qa:
        if math.floor(len(dia) / 2) == limit_turn_n:

            new_dia = []
            for qa in dia:
                if " robot" in qa:
                    qa = "robot: " + qa.split(" says:")[-1]

                if " user" in qa:
                    qa = "user: " + qa.split(" says:")[-1]
                new_dia.append(qa)

            re_dia_list.append(new_dia)

    return re_dia_list


if __name__ == '__main__':
    f_gpt4 = '/Users/jiahong/Downloads/bigolive_robot_chat_history.20230917.cot_gpt4.en.txt.1'
    f_gpt35 = '/Users/jiahong/Downloads/bigolive_robot_chat_history.20230917.cot_gpt35.en.txt.1'

    f_list = [f_gpt4, f_gpt35]

    save_f_list = [
        "/Users/jiahong/Downloads/test_gpt4.txt",
        "/Users/jiahong/Downloads/test_gpt35.txt",
    ]

    for f, save_f in zip(f_list, save_f_list):

        all_dialogue_qa = get_get_dialogue_qas(f)

        limit_turn_n = 30

        limit_re_dia = check_limit_turn_dialogue(all_dialogue_qa, limit_turn_n)

        print(f"大于 {limit_turn_n} 的对话有:{len(limit_re_dia)}")

        with open(save_f, 'w', buffering=1) as fw:
            for dia in limit_re_dia:
                for qa in dia:
                    fw.write(f"{qa}\n")
                fw.write("-" * 100 + "\n")

        print(f"save to:{save_f}")
