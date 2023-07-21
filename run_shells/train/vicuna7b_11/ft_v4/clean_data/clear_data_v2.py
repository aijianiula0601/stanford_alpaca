import json
import sys
from tqdm import tqdm
from clear_data import filter_specify_chat, toolong_check


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
    org_f = sys.argv[1]
    save_f = sys.argv[2]

    org_data_list = json.load(open(org_f))

    new_data_list = []
    skip_n = 1
    for example in tqdm(org_data_list):
        ex = process_example(example)
        if ex is not None:
            new_data_list.append(ex)
        else:
            skip_n += 1

    json.dump(new_data_list, open(save_f, 'w'))
    print(f"all_n:{len(org_data_list)},skip_n:{skip_n},now_n:{len(new_data_list)}")
    print(f"save to:{save_f}")
