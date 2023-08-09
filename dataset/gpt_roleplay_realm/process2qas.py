import os
import sys
import json
import pandas as pd
from pandas import read_parquet

# ---------------------------------------------------------------------
# 源链接：https://huggingface.co/datasets/IlyaGusev/gpt_roleplay_realm
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


def create_examples(row, index):
    bot_name = row['name'][index]
    human_name = "user"
    background = row['context'][index]

    dialogues = row['dialogues'][index]

    print("----dialogues:", dialogues['chat'])

    example_list = []
    for chat_example in dialogues:
        qas = {}
        for i, qa in enumerate(json.loads(chat_example['chat'])):
            if i % 2 == 0:
                role = qa['role']
                assert role == human_name
                question = qa['content']
            else:
                role = qa['role']
                assert role == "chat"
                answer = qa['content']
                qas[f"turn_{i // 2}"] = {"question": question, "answer": answer}

        example = {
            "background": background,
            "human_name": human_name,
            "bot_name": bot_name,
            "qas": qas,
        }
        example_list.append(example)

    return example_list


all_example_list = []
for index in df_data.index:
    res = df_data.loc[index]
    example_list = create_examples(row=res, index=index)
    all_example_list.extend(example_list)

print(f"all:{len(all_example_list)}")
json.dump(all_example_list, open(save_f, 'w'))
print(f"save to:{save_f}")
