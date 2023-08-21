import json
import os
import sys
import copy
from tqdm import tqdm

pdf = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.append(pdf)

from dataset.data_utils import *

# -----------------------------------------------------
# 单轮对话方式
# 1.单独保存第一轮作为一个对话
# 2.单独保存第二轮作为一个对话
# 3.单独保存第3~n轮作为一个对话
# -----------------------------------------------------


# v2
base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v2"
org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.en.txt"

org_data_list = open(org_f).readlines()

limit_chat_n = 260


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


def get_history(history: list, human_name: str, bot_name: str):
    history_qas = []
    for qa in history:
        qa_str = f"{DEFAULT_SEGMENT_TOKEN}{human_name}: {qa[QUESTION_KEY]} {DEFAULT_SEGMENT_TOKEN}{bot_name}: {qa[ANSWER_KEY]}"
        history_qas.append(qa_str)

    return '\n'.join(history_qas)


limit_turn0_dialogue_n = 10
limit_turn1_dialogue_n = 10

turn0_dialogue_data_list = []
turn1_dialogue_data_list = []
turn2ton_dialogue_data_list = []
who_ask_first = "user"
all_n = 0
skip_n = 0
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
            history_str = get_history(qa['history'], cur_example[HUMAN_NAME_KEY], cur_example[BOT_NAME_KEY])
            if i > 0:
                cur_example[
                    BACKGROUND_KEY] = f"{cur_example[BACKGROUND_KEY]}\nHere is our historical dialogue.\n{history_str}"

            new_qas = {"turn_0": {QUESTION_KEY: qa[QUESTION_KEY], ANSWER_KEY: qa[ANSWER_KEY]}}
            new_example = copy.deepcopy(cur_example)
            new_example[QAS_KEY] = new_qas

            cleaned_example = process_example(new_example)
            if cleaned_example is not None:
                cleaned_example[MASK_HEAD_KEY] = True
                cleaned_example[MASK_QUESTION_KEY] = True
                cleaned_example[MASK_EXCEPT_LAST_ANSWER] = False
                # fw.write(f"{json.dumps(cleaned_example)}\n")

            else:
                continue

            if i == 0 and len(qa['history']) <= 0:
                turn0_dialogue_data_list.append(cleaned_example)
                continue
            if i == 1:
                turn1_dialogue_data_list.append(cleaned_example)
                continue

            turn2ton_dialogue_data_list.append(cleaned_example)


    except Exception as e:
        skip_n += 1
        print(e)

print(f"all_n:{all_n},skip:{skip_n},exist:{all_n - skip_n}")

# -------------------
# 保存第一轮的对话
# -------------------
save_f = sys.argv[1]
with open(save_f, 'w', buffering=1) as fw:
    for example in turn0_dialogue_data_list:
        fw.write(f"{json.dumps(example)}\n")
print(f"turn0_dialogue_data_list:{len(turn0_dialogue_data_list)},save to:{save_f}")
# -------------------
# 保存第二轮的对话
# -------------------
save_f = sys.argv[2]
with open(save_f, 'w', buffering=1) as fw:
    for example in turn1_dialogue_data_list:
        fw.write(f"{json.dumps(example)}\n")
print(f"turn1_dialogue_data_list:{len(turn1_dialogue_data_list)},save to:{save_f}")
# -------------------
# 保存第3~n轮的对话
# -------------------
save_f = sys.argv[3]
with open(save_f, 'w', buffering=1) as fw:
    for example in turn2ton_dialogue_data_list:
        fw.write(f"{json.dumps(example)}\n")
print(f"turn2ton_dialogue_data_list:{len(turn2ton_dialogue_data_list)},save to:{save_f}")
