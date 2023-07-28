import json
import os
import sys
import string
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

punc = string.punctuation


def add_punc(sen_str: string):
    """句尾加标点"""
    if sen_str[-1] in punc:
        return sen_str
    else:
        return sen_str + "."


def process_conversation(conversation: list):
    # --------------------------
    # 合并单人说话
    # --------------------------
    from_value_example_list = []
    from_name = None
    value_list = []
    for i, fv in enumerate(conversation):
        cur_name = fv['from']
        cur_value = fv['value']
        if cur_name == from_name:
            value_list.append(add_punc(cur_value))
        else:
            if i > 0:
                from_value_example_list.append({"from": from_name, "value": '\n'.join(value_list)})
            from_name = cur_name
            value_list.clear()
            value_list.append(add_punc(cur_value))
    # --------------------------
    # 转换为qas格式
    # --------------------------
    human_name = from_value_example_list[0]['from']
    bot_name = from_value_example_list[1]['from']

    qas_dic = {}
    question = None
    for i, fv in enumerate(from_value_example_list):
        if i % 2 == 0:
            assert fv['from'] == human_name
            question = fv['value']
        else:
            assert fv['from'] == bot_name
            answer = fv['value']
            assert question is not None
            qa = {QUESTION_KEY: question, ANSWER_KEY: answer}
            qas_dic[f'turn_{i // 2}'] = qa

    return human_name, bot_name, qas_dic


def process_example(example_dic: dict):
    example_list = []
    background = example_dic['persona']
    for conv in example_dic['convs']:
        human_name, bot_name, qas_dic = process_conversation(conv)
        example_list.append({
            BACKGROUND_KEY: background,
            HUMAN_NAME_KEY: human_name,
            BOT_NAME_KEY: bot_name,
            DATASET_KEY: MECHAT_DATASET_NAME,
            QAS_KEY: qas_dic,
        })

    return example_list


if __name__ == '__main__':
    example_list = []
    base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/mechat"
    org_f = f'{base_dir}/mechat_conv_data.json'
    save_f = f'{base_dir}/mechat_conv_data_qas.json'
    f_data = json.load(open(org_f))
    for k in tqdm(f_data.keys()):
        for kk in f_data[k]:
            example_dic = f_data[k][kk]
            example_list.extend(process_example(example_dic))

    print(f"all_n:{len(example_list)}")
    json.dump(example_list, open(save_f, 'w'))
    print(f"save to:{save_f}")
