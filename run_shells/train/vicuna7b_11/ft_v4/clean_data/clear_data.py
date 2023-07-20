import json
import os
from tqdm import tqdm

limit_chat_n = 300


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


def process_example(example: dict):
    turn_n = len(example['qas'])

    qas = {}
    for i in range(turn_n):
        qa = example['qas'][f'turn_{i}']
        question = qa['question']
        answer = filter_specify_chat(qa['answer'])  # 过滤笑脸
        qa['answer'] = answer
        if toolong_check(answer):
            break
        qas[f'turn_{i}'] = {"question": question, "answer": answer}

    example["qas"] = qas

    return example


if __name__ == '__main__':
    base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4"
    org_f = f"{base_dir}/train_data.json"
    save_f = f"{base_dir}/cleaned_train_data.json"

    org_data_list = json.load(open(org_f))

    new_data_list = []
    for example in tqdm(org_data_list):
        ex = process_example(example)
        new_data_list.append(ex)

    json.dump(new_data_list, open(save_f, 'w'))
    print(f"save to:{save_f}")
