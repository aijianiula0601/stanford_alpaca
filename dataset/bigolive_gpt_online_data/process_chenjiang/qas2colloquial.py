import json
import random
import os
import time
import sys
from tqdm import tqdm

# ---------------------------------------
# 把聊天数据修改得更加口语化，并加上表情
# ---------------------------------------

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdf)

from dataset.filter_ops import *

# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "548e5c0c2aff453e932948927a27bde6"

# role : system|user|assistant
gpt_config = {'engine': 'gpt-35-turbo',
              'role': 'user',
              }

requirement_str2 = "Be careful not to change the meaning of the sentence while speaking colloquially, don't always speak in a flirty tone, and don't take it upon yourself to add greeting words."

prompt_background = (
    "Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. "
    "Be careful not to change the meaning of the sentence while speaking colloquially, don't always speak in a flirty tone, and don't take it upon yourself to add greeting words. "
    "you can add some modal auxiliary words to the front of the sentence according to the meaning of the sentence, such as Um... "

)


def qa_colloquial(qa_str: str):
    """给gpt35改为口语化表达"""
    message_list = [
        {"role": "system",
         "content": prompt_background},
        {"role": "user", "content": f"{qa_str}"}
    ]

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=0.7,
        messages=message_list
    )
    return response['choices'][0]['message']['content']


def trans_example_qas(example: dict):
    """把所有回复拼接好，然后传给gpt35改造为口语化"""
    answer_list = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        answer_list.append(qa['answer'].replace("\n", ""))

    qas_str = "\n".join(answer_list)
    colloquial_answer_str = qa_colloquial(qas_str)
    colloquial_answer_list = colloquial_answer_str.split("\n")
    if len(colloquial_answer_list) != len(example['qas']):  # 验证转换后的语句个数是否跟原来的一致
        return None

    # 过滤露馅问题
    filtered_qas = filter_qa(example['qas'])
    if filtered_qas is None:
        return None

    example['qas'] = filtered_qas

    for i in range(len(example['qas'])):
        qa = example['qas'][f"turn_{i}"]
        qa['colloquial_answer'] = colloquial_answer_list[i]

    return example


if __name__ == '__main__':
    base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data"
    org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.txt"
    save_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user_to_colloquial.txt"

    org_data_list = open(org_f).readlines()
    random.shuffle(org_data_list)
    with open(save_f, 'a', buffering=1) as fw:
        for line in tqdm(org_data_list):
            try:
                example = json.loads(line)
                rw_example = trans_example_qas(example)
                if rw_example is not None:
                    fw.write(f"{json.dumps(rw_example)}\n")
                    time.sleep(15)

            except Exception as e:
                print(e)
                pass
