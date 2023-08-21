import os
import sys
import json
import copy
import traceback

pdf = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print("----pdr:", pdf)
sys.path.append(pdf)

from dataset.bigolive_gpt_online_data.process_chenjiang.process2qas_robot import *


# ---------------------------
# 把口语化的数据改为单轮对话方式
# ---------------------------


def process_example_f(example):
    """
    1.把原来dic的qas改为list方式
    2.口语化的回复覆盖原来的回复
    3.之前的历史也改为口语化的历史
    """

    qas_list = []
    for i in range(len(example[QAS_KEY])):
        qa = example[QAS_KEY][f"{TURN_KEY}_{i}"]
        answer = qa[ANSWER_KEY]
        colloquial_answer = qa['colloquial_answer']

        qa["org_answer"] = answer
        qa[ANSWER_KEY] = colloquial_answer
        del qa['colloquial_answer']

        qas_list.append(qa)

    for i, qa in enumerate(qas_list):
        history_l = len(qa['history'])
        qa['history'] = qas_list[min(0, i - history_l):i]

        cp_qa_h = copy.deepcopy(qa['history'])
        for h_qa in cp_qa_h:
            if 'history' in h_qa:
                del h_qa['history']
            if 'org_answer' in h_qa:
                del h_qa['org_answer']
        qa['history'] = cp_qa_h

    example[QAS_KEY] = qas_list

    return example


def get_history(history: list, human_name: str, bot_name: str):
    history_qas = []
    for qa in history:
        qa_str = f"{DEFAULT_SEGMENT_TOKEN}{human_name}: {qa[QUESTION_KEY]} {DEFAULT_SEGMENT_TOKEN}{bot_name}: {qa[ANSWER_KEY]}"
        history_qas.append(qa_str)

    return '\n'.join(history_qas)


if __name__ == '__main__':

    # 口语化数据文件路径：/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v2/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.en_to_colloquial.txt
    org_f = sys.argv[1]
    # 保存为单轮的文件路径
    save_f_turns = sys.argv[2]

    who_ask_first = "user"
    all_n = 0
    skip_n = 0
    with open(save_f_turns, 'w', buffering=1) as fw:
        with open(org_f) as fr:
            for line in tqdm(fr.readlines()):
                all_n += 1
                try:
                    cur_example = process_example_f(json.loads(line))
                    assert cur_example[
                               'who_ask_first'] == who_ask_first, f"error who ask first, {cur_example['who_ask_first']}!={who_ask_first}, example:{example}"
                    del cur_example['who_ask_first']
                    cur_example[BACKGROUND_KEY] = BIGOLIVE_CHAT_ROBOT
                    cur_example[BACKGROUND_KEY] = cur_example['prompt']
                    del cur_example['prompt']
                    for i, qa in enumerate(cur_example["qas"]):

                        history_str = get_history(qa['history'], cur_example[HUMAN_NAME_KEY], cur_example[BOT_NAME_KEY])
                        if i > 0:
                            cur_example[BACKGROUND_KEY] = f"{cur_example[BACKGROUND_KEY]}\n{history_str}"

                        new_qas = {"turn_0": {QUESTION_KEY: qa[QUESTION_KEY], ANSWER_KEY: qa[ANSWER_KEY]}}
                        new_example = copy.deepcopy(cur_example)
                        new_example[QAS_KEY] = new_qas

                        cleaned_example = process_example(new_example)
                        if cleaned_example is not None:
                            cleaned_example[MASK_HEAD_KEY] = True
                            cleaned_example[MASK_QUESTION_KEY] = True
                            cleaned_example[MASK_EXCEPT_LAST_ANSWER] = False
                            fw.write(f"{json.dumps(cleaned_example)}\n")

                except Exception as e:
                    skip_n += 1
                    print(f"Error example:{line},{e}")
                    traceback.print_exc()

    print(f"all_n:{all_n},skip:{skip_n},exist:{all_n - skip_n},save to:{save_f_turns}")
