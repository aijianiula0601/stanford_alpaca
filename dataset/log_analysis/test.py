import json
from copy import deepcopy
from tqdm import tqdm
import copy


def process_dialogue(dialogue_lines: list):
    dialogue_lines_len = len(dialogue_lines)

    seq_id_list = []

    for i in range(dialogue_lines_len):
        line = dialogue_lines[i]

        if "seq_id=" in line:
            seq_id_list.append(line.split("says:")[-1])

    if len(seq_id_list) > 1:
        qa_str = ' '.join(seq_id_list[1:])
        print("----qas_str:", qa_str)

        if 'WhatsApp'.lower() in qa_str.lower():
            return True, len(seq_id_list)

    return False, len(seq_id_list)


def get_dialogue_lines(file_name):
    all_dialogue_lines = []

    dialogue_lines = []
    with open(file_name) as fr:
        for line in fr:
            line = line.replace("\n", "")
            if line.strip() == '------------------------------':
                all_dialogue_lines.append(deepcopy(dialogue_lines))
                dialogue_lines.clear()
            else:
                dialogue_lines.append(line)

    return all_dialogue_lines


if __name__ == '__main__':
    fp = '/Users/jiahong/Library/Containers/com.tencent.WeWorkMac/Data/Documents/Profiles/B7B28C02E7C396716ACE2C633FA37E42/Caches/Files/2023-10/aeee1126297be3665240ef14b63cb761/bigolive_robot_chat_history.20231008am.en.txt'
    all_dialogue_lines = get_dialogue_lines(fp)

    save_f = "/Users/jiahong/Downloads/test.txt"

    flag_list = []
    seq_id_n_list = []
    for dls in tqdm(all_dialogue_lines):
        whats_app_flag, seq_id_n = process_dialogue(dls)
        seq_id_n_list.append(seq_id_n)
        flag_list.append(whats_app_flag)

    whatsapp_dialogue_n = flag_list.count(True)
    more1_d_n = sum([1 if n > 1 else 0 for n in seq_id_n_list])
    print(f"对话个数:{len(seq_id_n_list)},有回复的:{more1_d_n},询问Whatsapp的对话数:{whatsapp_dialogue_n}")

    print(
        f"所有对话中占比:{round(whatsapp_dialogue_n / len(flag_list) * 100, 3)}%，有回复中的占比:{round(whatsapp_dialogue_n / more1_d_n * 100, 3)}%")
