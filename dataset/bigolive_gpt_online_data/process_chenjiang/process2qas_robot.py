import json
import os
import sys
import copy
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)

from dataset.data_utils import *

# -----------------------------------------------------
# 机器人接待，用户先发问
# 分为两种方式清洗数据
# 1.整个对话方式
# 2.把历史信息放到prompt中
# -----------------------------------------------------


limit_chat_n = 250


def toolong_check(answer):
    """
    超过指定长度检测
    """
    if len(answer) > limit_chat_n:
        return True
    else:
        return False


def filter_specify_chat(answer: str):
    return answer.strip().rstrip(":)").rstrip(" :)")


def limit_question_n(answer: str):
    """
    限制问号出现的次数
    """
    qn = answer.count("?")

    if qn > 1:
        return True

    return False


def process_example(example: dict):
    turn_n = len(example['qas'])

    qas = {}
    for i in range(turn_n):
        qa = example['qas'][f'turn_{i}']
        question = qa['question']
        answer = filter_specify_chat(qa['answer'])  # 过滤笑脸
        qa['answer'] = answer
        if toolong_check(answer) or limit_question_n(answer):
            break
        qas[f'turn_{i}'] = {"question": question, "answer": answer}

    if len(qas) < 1:
        return None

    example["qas"] = qas

    return example


if __name__ == '__main__':

    # v1
    # base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data"
    # org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.txt"
    # save_f_dialogue = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user#robot_dialogue_qas.txt"
    # save_f_turns = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user#robot_turns_qas.txt"

    # v2
    base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v2"
    org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.en.txt"
    save_f_dialogue = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.en#robot_dialogue_qas.txt"
    save_f_turns = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.en#robot_turns_qas.txt"

    org_data_list = open(org_f).readlines()

    # ---------------------
    # 整个对话方式
    # ---------------------

    who_ask_first = "user"
    all_n = 0
    skip_n = 0
    with open(save_f_dialogue, 'w', buffering=1) as fw:
        for example in tqdm(org_data_list):
            all_n += 1

            try:
                cur_example = json.loads(example)
                assert cur_example[
                           'who_ask_first'] == who_ask_first, f"error who ask first, {cur_example['who_ask_first']}!={who_ask_first}, example:{example}"
                del cur_example['who_ask_first']
                cur_example[BACKGROUND_KEY] = BIGOLIVE_CHAT_ROBOT
                cur_example[BACKGROUND_KEY] = cur_example['prompt']
                del cur_example['prompt']
                for i in range(len(cur_example[QAS_KEY])):
                    qa = cur_example[QAS_KEY][f'turn_{i}']
                    del qa['history']

                cleaned_example = process_example(cur_example)
                if cleaned_example is not None:
                    cleaned_example[MASK_HEAD_KEY] = True
                    cleaned_example[MASK_QUESTION_KEY] = True
                    cleaned_example[MASK_EXCEPT_LAST_ANSWER] = False
                    fw.write(f"{json.dumps(cleaned_example)}\n")
            except Exception as e:
                skip_n += 1
                print(e)

    print(f"all_n:{all_n},skip:{skip_n},exist:{all_n - skip_n},save to:{save_f_dialogue}")


    # ---------------------
    # 单轮对话方式
    # ---------------------

    def get_history(history: list, human_name: str, bot_name: str):
        history_qas = []
        for qa in history:
            qa_str = f"{DEFAULT_SEGMENT_TOKEN}{human_name}: {qa[QUESTION_KEY]} {DEFAULT_SEGMENT_TOKEN}{bot_name}: {qa[ANSWER_KEY]}"
            history_qas.append(qa_str)

        return '\n'.join(history_qas)


    who_ask_first = "user"
    all_n = 0
    skip_n = 0
    with open(save_f_turns, 'w', buffering=1) as fw:
        for example in tqdm(org_data_list):
            all_n += 1

            try:
                cur_example = json.loads(example)
                assert cur_example[
                           'who_ask_first'] == who_ask_first, f"error who ask first, {cur_example['who_ask_first']}!={who_ask_first}, example:{example}"
                del cur_example['who_ask_first']
                cur_example[DATASET_KEY] = BIGOLIVE_CHAT_ROBOT
                for i in range(len(cur_example[QAS_KEY])):
                    cur_example[BACKGROUND_KEY] = cur_example['prompt']
                    qa = cur_example[QAS_KEY][f'turn_{i}']
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
                print(e)

    print(f"all_n:{all_n},skip:{skip_n},exist:{all_n - skip_n},save to:{save_f_turns}")
