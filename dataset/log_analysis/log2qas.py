import json
from copy import deepcopy
from tqdm import tqdm
import copy


def process_dialogue(dialogue_lines: list):
    background_str = None

    qa_list = []
    qa_name_list = []
    dialogue_lines_len = len(dialogue_lines)
    for i in range(dialogue_lines_len):
        line = dialogue_lines[i]
        if "role:" in line:
            background_str = dialogue_lines[i + 1]
            i += 1
            continue

        if "seq_id=" in line and 'says:' in line:
            qa_res = line.split(" says:")[-1].strip()
            if ' robot ' in line:
                say_name = 'robot'
            else:
                say_name = "user"

            qa_list.append(qa_res)
            qa_name_list.append(say_name)

    qas = []
    qa = {}
    a_i = 0
    for i, (qa_rs, sn) in enumerate(zip(qa_list, qa_name_list)):
        if sn == 'robot':
            if len(qa) > 0:
                qas.append(deepcopy(qa))
                qa.clear()
            qa['robot_q'] = qa_rs
            a_i = 0
        else:
            qa[f'user_a_{a_i}'] = qa_rs
            a_i += 1

    if len(qa) > 0:
        qas.append(qa)

    return {"background": background_str, 'qas': qas}


def get_dialogue_lines(file_name):
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


if __name__ == '__main__':
    fp = "/Users/jiahong/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/B7B28C02E7C396716ACE2C633FA37E42/Caches/Files/2023-09/412af347fa176ccc24114672fc08f82d/bigolive_robot_chat_history.20230917.cot_gpt35.en.txt"
    all_dialogue_lines = get_dialogue_lines(fp)

    save_f = "/Users/jiahong/Downloads/test.txt"

    with open(save_f, 'w', buffering=1) as fw:
        for dls in tqdm(all_dialogue_lines):
            example = process_dialogue(dls)
            fw.write(f"{json.dumps(example)}\n")

    print(f"save to:{save_f}")
