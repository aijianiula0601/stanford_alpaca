import os
import sys
import json

# ----------------------------------------------------------------------------
#  处理永强用gpt35调回来的数据
#  永强数据存储目录：
#   /mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data
# ----------------------------------------------------------------------------


pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

# ----------------------------------
# from-value转换为qas格式
# ----------------------------------
HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"


def trans2qa(all_data, dataset_name):
    new_data = []
    skip_n = 0
    for turns_data in all_data:
        background = None
        qas = {}
        human_name = turns_data[0]['from']
        bot_name = turns_data[1]['from']
        turn_i = 0

        try:
            for i, td in enumerate(turns_data):
                if i == 0:
                    background = td['background']
                if (i + 1) % 2 == 1:
                    assert human_name == td['from'], f"error qas:{json.dumps(turns_data)}"
                    qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
                else:
                    assert bot_name == td['from']
                    qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value'].strip()
                    turn_i += 1
        except Exception as e:
            skip_n += 1
            continue

        turn_n = len(qas)
        if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
            qas.pop(f"turn_{turn_n - 1}")

        if len(qas) < 1:
            continue

        assert background is not None
        new_data.append(
            {BACKGROUND_KEY: background,
             DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})

    print(f"----skip qas nums:{skip_n},all_n:{len(new_data)}")

    return new_data


def process_f(f, save_f, dataset_name):
    data_list = json.load(open(f))
    new_data_list = []
    for qas in data_list:
        for i, qa in enumerate(qas[1:]):
            if i == 0:
                qa[BACKGROUND_KEY] = qa['BACKGROUD_B']
                del qa['BACKGROUD_A']
                del qa['BACKGROUD_B']
            else:
                break
        new_data_list.append(qas[1:])

    qas_data_list = trans2qa(new_data_list, dataset_name=dataset_name)
    json.dump(qas_data_list, open(save_f, 'w'))
    print(f"save to:{save_f}")


if __name__ == '__main__':
    org_base_dir = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data"
    save_base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/yongqiaong_gpt35sex_data"

    f_list = [
        f"{org_base_dir}/sexy_chat_prompt_1_2_2020.json",
        f"{org_base_dir}/sexy_chat_prompt_3_2000_Jamie_check_random_prompt.json",
        f"{org_base_dir}/azure_sexy_chat_4_793_randomprompt.json",
        f"{org_base_dir}/azure_sexy_chat_5_500_randomprompt.json",
    ]

    for org_f in f_list:
        print(f'org_f:{org_f}')
        save_f = f"{save_base_dir}/{os.path.basename(org_f).replace('.json', '_qas.json')}"
        process_f(org_f, save_f, dataset_name=GPT35_DATASET_NAME)
        print("-" * 100)
