import json
import random


def get_right_data(f):
    data_dic = json.load(open(f))
    new_data_dic = {}
    all_n = 0
    skip_n = 0
    for k in data_dic:
        example = data_dic[k]
        assert "prompt" in example and "human_name" in example and "bot_name" in example and "qas" in example, f"error:\n{json.dumps(example)}"
        all_n += 1
        skip_flag = False
        for qa in example['qas']:

            assert "question" in qa and "answer" in qa
            if qa['question'].strip() == "" or qa["answer"].strip() == "":
                skip_n += 1
                skip_flag = True
                # print("*" * 100)
                # print(f"Error, example: key:{k}, data:{json.dumps(example)} ")
                # print("*" * 100)
                break
        if skip_flag:
            continue
        new_data_dic[k] = example

    print("-" * 100)
    print(f"all_n:{all_n},存在空回复的数据为:{skip_n},f:{f}")
    print("-" * 100)

    return new_data_dic


if __name__ == '__main__':
    test_f = "test_model_dialogues20230608.json"
    test_f_v2 = "test_model_dialogues20230608_v2.json"
    all_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230607.json"

    test_data_dic = get_right_data(test_f)
    all_data_dic = get_right_data(all_f)

    all_data_dic_keys = list(all_data_dic.keys())
    random.shuffle(all_data_dic_keys)

    i = 0
    limit_n = 7
    for k in all_data_dic_keys[:100]:
        if len(all_data_dic[k]['qas']) >= 5 and k not in test_data_dic:
            test_data_dic[k] = all_data_dic[k]
            i += 1
        if i >= limit_n:
            break
    json.dump(test_data_dic, open(test_f_v2, 'w'))
    print(f"test k:{len(test_data_dic)}")
