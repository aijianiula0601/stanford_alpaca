import json
import random
import time
from tqdm import tqdm
# ---------------------------------------
# 把聊天数据修改得更加口语化，并加上表情
# ---------------------------------------


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

requirement_str1 = "If the sentence is emotional, add emojis that match human emotions. Depending on the meaning of the sentence, it is necessary to add emojis only when there is an emotional expression."
requirement_str2 = "Be careful not to change the meaning of the sentence while speaking colloquially, don't always speak in a flirty tone, and don't take it upon yourself to add greeting words."

prompt_background_list = [
    f"Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. {requirement_str1} {requirement_str2}",
    f"Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. {requirement_str1} Modify or add some modal words according to the meaning of the sentence. {requirement_str2}",
]

print("-" * 100)
print(f"prompt:{prompt_background_list}")
print("-" * 100)


def qa_colloquial(qa_str: str):
    """给gpt35改为口语化表达"""
    message_list = [
        {"role": "system",
         "content": random.sample(prompt_background_list, k=1)[0]},
        {"role": "user", "content": f"{qa_str}"}
    ]

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content']


def trans_example_qas(example: dict):
    """所有的qa一起送进去gpt35改成口语化表达,测试过，这种方式转换更好。"""
    qas_list = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        qas_list.append(qa['question'].replace("\n", ""))
        qas_list.append(qa['answer'].replace("\n", ""))

    qas_str = "\n".join(qas_list)
    colloquial_qas_str = qa_colloquial(qas_str)
    colloquial_qas_list = colloquial_qas_str.split("\n")
    # 分组
    colloquial_qas_list = [colloquial_qas_list[i:i + 2] for i in range(0, len(colloquial_qas_list), 2)]
    if len(colloquial_qas_list) != len(example['qas']):
        return None

    for i in range(len(colloquial_qas_list)):
        qa = example['qas'][f"turn_{i}"]
        qa['org_question'] = qa['question']
        qa['org_answer'] = qa['answer']
        qa['question'] = colloquial_qas_list[i][0]
        qa['answer'] = colloquial_qas_list[i][1]

    return example


def trans_example_qa(example: dict):
    """每个qa单独送进去gpt35改成口语化表达，由于是单个句子转换没有上下文，测试时发现转换的句子意思会有偏差"""
    for i in range(len(example['qas'])):
        qa = example['qas'][f"turn_{i}"]
        qa['org_question'] = qa['question']
        qa['org_answer'] = qa['answer']
        qa['question'] = qa_colloquial(qa['question'])
        qa['answer'] = qa_colloquial(qa['answer'])

    return example


def filter_long_answer(data_list: list, limit_char_n: int, limit_turn_n: int = 5):
    print("filtering long qa...")

    def if_long(qa_str):
        if len(qa_str) > limit_char_n:
            return True
        else:
            return False

    short_qs_example_list = []
    all_n = 0
    skip_n = 0
    for example in tqdm(data_list):
        all_n += 1

        qas_dic = {}
        for i in range(len(example['qas'])):
            qa = example['qas'][f"turn_{i}"]
            if not if_long(qa['question']) and not if_long(qa['answer']) and i < limit_turn_n:
                qas_dic[f'turn_{i}'] = {'question': qa['question'], "answer": qa["answer"]}
            else:
                break
        if len(qas_dic) > 0:
            example['qas'] = qas_dic
            short_qs_example_list.append(example)
        else:
            skip_n += 1

    print(f"all_n:{all_n},skip_n:{skip_n},now_n:{len(short_qs_example_list)}")

    return short_qs_example_list


if __name__ == '__main__':
    base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda"
    org_f = f"{base_dir}/soda_train_name_qas_filter_sometion.json"
    save_f = f"{base_dir}/soda_train_name_qas_filter_sometion_to_colloquial.txt"

    org_data_list = json.load(open(org_f))
    data_list = filter_long_answer(org_data_list, limit_char_n=200)

    with open(save_f, 'w', buffering=1) as fw:
        for example in tqdm(data_list):
            try:
                # rw_example = trans_example_qa(example)
                rw_example = trans_example_qas(example)
                if rw_example is not None:
                    fw.write(f"{json.dumps(rw_example)}\n")

            except Exception as e:
                print(e)
                pass
