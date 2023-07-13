import json
import os
import sys
from pathlib import Path

# 数据集地址：https://huggingface.co/datasets/QingyiSi/Alpaca-CoT/tree/main/Chain-of-Thought/formatted_cot_data

pfd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pfd:{pfd}")
sys.path.append(pfd)

from dataset.data_utils import *


def instruction2example(item: dict):
    if item['input'].strip() == "":
        question_str = item['instruction']
    else:
        question_str = item['instruction'] + "\n" + DEFAULT_SEGMENT_TOKEN + INPUT_NAME + ":" + item['input']

    example = {
        BACKGROUND_KEY: item['input'],
        DATASET_KEY: INSTRUCTION_INPUT_DATASET_NAME,
        HUMAN_NAME_KEY: INSTRUCTION_NAME,
        BOT_NAME_KEY: RESPONSE_NAME,
        QAS_KEY: {
            "turn_0": {
                QUESTION_KEY: question_str,
                ANSWER_KEY: item['output']}
        }
    }

    return example


base_dir = sys.argv[1]  # 传输执行的目录如：/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/auto-cot
save_base_dir = f"{base_dir}/qas"
os.system(f"rm -rf {save_base_dir} && mkdir -p {save_base_dir}")

for org_f in Path(base_dir).glob("*.json"):
    example_list = []
    print('-' * 100)
    print(f"reading:{org_f}")
    instruction_data = json.load(open(org_f))

    for item in instruction_data:
        try:
            example = instruction2example(item)
            example_list.append(example)
        except Exception as e:
            print(e)
            print(f"Error item:{item}")

    print(f"all_N:{len(example_list)}")
    save_f = f"{save_base_dir}/{Path(org_f).name.replace('.json', '_qas.json')}"
    json.dump(example_list, open(save_f, 'w'))
    print(f"save to:{save_f}")
