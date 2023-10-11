import random
from copy import deepcopy


def get_dialogue_lines(file_name):
    """
    采用分割线把整个对话切分出来
    """

    all_dialogue_lines = []

    dialogue_lines = []
    with open(file_name) as fr:
        for line in fr:
            line = line.strip("\n")
            if line.strip() == '------------------------------':
                all_dialogue_lines.append(deepcopy(dialogue_lines))
                dialogue_lines.clear()
            else:
                dialogue_lines.append(line)

    return all_dialogue_lines


def get_get_dialogue_qas(file_name):
    """
    只提取qa
    """
    all_dialogue_qa = []

    dialogue_qa = []
    with open(file_name) as fr:
        for line in fr:
            line = line.strip("\n")
            if line.strip() == '------------------------------':
                all_dialogue_qa.append(deepcopy(dialogue_qa))
                dialogue_qa.clear()
            else:

                if line.startswith("seq_id="):
                    dialogue_qa.append(line)

    return all_dialogue_qa


if __name__ == '__main__':
    f = "/Users/jiahong/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/B7B28C02E7C396716ACE2C633FA37E42/Caches/Files/2023-10/17518fdfa98c1a39a67970ca93658471/bigolive_robot_chat_history.20230918.cot_gpt35.en.txt"

    all_dialogue_qa = get_get_dialogue_qas(f)

    for dqa in all_dialogue_qa:
        if len(dqa) > 10:
            for qa in dqa:
                print(qa)
            break
