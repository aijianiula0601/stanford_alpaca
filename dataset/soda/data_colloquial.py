import json
import random
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

prompt_background_list = [
    "Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. If the sentence is emotional, add emojis that match human emotions.",
    "Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. If the sentence is emotional, add emojis that match human emotions. Modify or add some modal words according to the meaning of the sentence.",
]


def qa_colloquial(qa_str: str):
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


def trans_example(example: dict):
    for i in range(len(example['qas'])):
        qa = example['qas'][f"turn_{i}"]
        qa['org_question'] = qa['question']
        qa['org_answer'] = qa['answer']
        qa['question'] = qa_colloquial(qa['question'])
        qa['answer'] = qa_colloquial(qa['answer'])

    return example


if __name__ == '__main__':
    base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/soda"
    org_f = f"{base_dir}/soda_train_name_qas_filter_sometion.json"
    save_f = f"{base_dir}/soda_train_name_qas_filter_sometion_to_colloquial.txt"

    with open(save_f, 'w', buffering=1) as fw:
        for example in tqdm(json.load(open(org_f))):
            try:
                rw_example = trans_example(example)
                fw.write(f"{json.dumps(rw_example)}\n")
            except Exception as e:
                print(e)
                pass
