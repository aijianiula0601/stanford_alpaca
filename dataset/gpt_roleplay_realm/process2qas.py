import os
import sys
import json
import pandas as pd
from pandas import read_parquet

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

# ---------------------------------------------------------------------
# 源链接：https://huggingface.co/datasets/IlyaGusev/gpt_roleplay_realm
# 一共有216个角色，每个角色有20个对话。
# ---------------------------------------------------------------------


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/gpt_roleplay_realm"
org_f = f"{base_dir}/en-00000-of-00001-6291ef0dc79c47ed.parquet"
save_f = f"{base_dir}/en-00000-of-00001-6291ef0dc79c47ed_qas.json"

data = read_parquet(org_f)
print(data.count())
print('-' * 20)
print(data.head())
print('-' * 20)

df_data = read_parquet(org_f,
                       columns=['name', 'context', 'greeting', 'example_dialogue', 'topics', 'dialogues', 'char_id'])

user_ask_first_n = 0
bot_ask_first_n = 0
background_n_dic = {}


def create_examples(row, index):
    global user_ask_first_n
    global bot_ask_first_n
    bot_name = row['name'][index]
    human_name = "user"
    background = row['context'][index].strip()

    dialogues = row['dialogues'][index]

    example_list = []
    for chat_example in dialogues:
        background_n_dic[background] = background_n_dic.get(background, 0) + 1
        try:
            # -----------------
            # 用户先开始发问的
            # -----------------
            qas = {}
            for i, qa in enumerate(chat_example['chat']):
                if i % 2 == 0:
                    role = qa['role']
                    assert role == human_name, f"error user role_name:{role},chat:{chat_example['chat']}"
                    question = qa['content']
                else:
                    role = qa['role']
                    assert role == "char", f"error content role_name:{role},chat:{chat_example['chat']}"
                    answer = qa['content']
                    qas[f"turn_{i // 2}"] = {"question": question, "answer": answer}

            example = {
                BACKGROUND_KEY: background,
                HUMAN_NAME_KEY: human_name,
                BOT_NAME_KEY: bot_name,
                MASK_HEAD_KEY: True,
                MASK_QUESTION_KEY: True,
                MASK_EXCEPT_LAST_ANSWER: False,
                QAS_KEY: qas,
            }
            example_list.append(example)
            user_ask_first_n += 1
        except Exception as e:
            bot_ask_first_n += 1
            # -----------------
            # 角色先开始发问的
            # -----------------
            qas = {}
            for i, qa in enumerate(chat_example['chat']):
                if i % 2 == 0:
                    role = qa['role']
                    assert role == 'char', f"error user role_name:{role},chat:{chat_example['chat']}"
                    question = qa['content']
                else:
                    role = qa['role']
                    assert role == human_name, f"error content role_name:{role},chat:{chat_example['chat']}"
                    answer = qa['content']
                    qas[f"turn_{i // 2}"] = {"question": question, "answer": answer}

            example = {
                BACKGROUND_KEY: background,
                HUMAN_NAME_KEY: human_name,
                BOT_NAME_KEY: bot_name,
                MASK_HEAD_KEY: True,
                MASK_QUESTION_KEY: False,
                MASK_EXCEPT_LAST_ANSWER: False,
                QAS_KEY: qas,
            }
            example_list.append(example)

    return example_list


all_example_list = []
for index in df_data.index:
    example_list = create_examples(row=df_data, index=index)
    all_example_list.extend(example_list)

print(f"---共有:{len(background_n_dic)}个角色")
print("---每个角色有多少个对话:", [background_n_dic[k] for k in background_n_dic])
print(f"all:{len(all_example_list)},user_ask_first_n:{user_ask_first_n},bot_ask_first_n:{bot_ask_first_n}")
json.dump(all_example_list, open(save_f, 'w'))
print(f"save to:{save_f}")
