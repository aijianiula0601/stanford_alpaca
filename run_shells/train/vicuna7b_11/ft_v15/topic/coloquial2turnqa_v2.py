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
        org_qa = example[QAS_KEY][f"{TURN_KEY}_{i}"]

        qa = copy.deepcopy(org_qa)

        answer = qa[ANSWER_KEY]
        colloquial_answer = qa['colloquial_answer']

        qa["org_answer"] = answer
        qa[ANSWER_KEY] = colloquial_answer
        del qa['colloquial_answer']

        qas_list.append(qa)

    for i, qa in enumerate(qas_list):
        history_l = len(qa['history'])
        qa['history'] = qas_list[max(0, i - history_l):i]

        # 暂时处理
        if history_l != len(qa['history']):
            return None

        assert history_l == len(qa[
                                    'history']), f"org_history_l:{history_l},now:{len(qa['history'])}，error_turn_i:{i},\norg_example:{json.dumps(example)}\nqa:{json.dumps(qa)}"

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


additional_prompt = "Responce without keyword including \"AI\", \"language model\", \"virtual assistant\" and within 20 words. You need to immerse yourself in your role not chat assistant. -If user asks you to make voice call, share pictures or videos, share position, say you are not quite familiar with each other yet and shift the conversation to a different topic. -If user ask you for accounts other platforms like WhatsApp, say you are still in the process of getting to know each other and explore a different topic. -If user think you are robot, you must refuse to express anger and attempt to end the conversation. -When a user expresses affection towards you, you can politely express your gratitude and suggest getting to know each other better. Response to the recent user sentence."
conversation_str = "The following a conversation you had with someone."
colloquial_prompt = "You should answer in a colloquial way."

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
                cur_example = process_example_f(json.loads(line))
                if cur_example is None:
                    skip_n += 1
                    continue
                assert cur_example[
                           'who_ask_first'] == who_ask_first, f"error who ask first, {cur_example['who_ask_first']}!={who_ask_first}, example:{example}"
                del cur_example['who_ask_first']
                cur_example[DATASET_KEY] = BIGOLIVE_ONLINE_CHAT_DATASET_NAME
                for i, qa in enumerate(cur_example["qas"]):
                    cur_example[BACKGROUND_KEY] = cur_example['prompt']

                    history_str = get_history(qa['history'], cur_example[HUMAN_NAME_KEY], cur_example[BOT_NAME_KEY])

                    if len(qa['history']) > 3:
                        print("-------ll:", history_str)

                    additional_prompt_str = f" {additional_prompt}" if cur_example[
                                                                           "exp_tag"] == "prompt_optimize" else ""
                    if i > 0:
                        cur_example[
                            BACKGROUND_KEY] = f"{cur_example[BACKGROUND_KEY]} {colloquial_prompt}{additional_prompt_str}\n{conversation_str}\n{history_str}"
                    else:
                        cur_example[
                            BACKGROUND_KEY] = f"{cur_example[BACKGROUND_KEY]} {colloquial_prompt}{additional_prompt_str}\n{conversation_str}\n"

                    new_qas = {"turn_0": {QUESTION_KEY: qa[QUESTION_KEY], ANSWER_KEY: qa[ANSWER_KEY]}}
                    new_example = copy.deepcopy(cur_example)
                    del new_example['prompt']
                    new_example[QAS_KEY] = new_qas

                    cleaned_example = process_example(new_example)
                    if cleaned_example is not None:
                        cleaned_example[MASK_HEAD_KEY] = True
                        cleaned_example[MASK_QUESTION_KEY] = True
                        cleaned_example[MASK_EXCEPT_LAST_ANSWER] = False
                        fw.write(f"{json.dumps(cleaned_example)}\n")

    print(f"all_n:{all_n},skip:{skip_n},exist:{all_n - skip_n},save to:{save_f_turns}")
