import os
import sys
import json
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pdf}")
sys.path.append(pdf)

from dataset.data_utils import *

# 下载地址：https://raw.githubusercontent.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM/main/data/alpaca_gpt4_data.json
# 原地址：https://github.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM#data-release


# ---------------------------------------------
# 处理成如下个数：
#  qa数据中一个example为：
#   {
#         "background":"---",
#         "human_name":"a",
#         "bot_name":"b",
#         "qas":{
#             "turn_0":{"question":"---","answer":"---"},
#             ...
#             "turn_n":{"question":"---","answer":"---"}
#         }
#   }
# ---------------------------------------------
# ---------------------------------------------
# 原始数据
# ---------------------------------------------


base_dir = '/mnt/cephfs/hjh/common_dataset/nlp/instruction/WizardLM_WizardLM_evol_instruct_70k'
org_f = f"{base_dir}/alpaca_evol_instruct_70k.json"
save_f = f"{base_dir}/alpaca_evol_instruct_70k_qas.txt"

org_data = json.load(open(org_f))

background = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."

with open(save_f, 'w') as fw:
    for item in tqdm(org_data):
        input_str = item["input"] if 'input' in item else ""
        assert input_str == ""
        cur_example = {DATASET_KEY: WIZARDLM_EVOL_INSTRUNCT,
                       BACKGROUND_KEY: background,
                       HUMAN_NAME_KEY: HUMAN_DEFAULT_NAME,
                       BOT_NAME_KEY: BOT_DEFAULT_NAME,
                       MASK_HEAD_KEY: True,
                       MASK_QUESTION_KEY: True,
                       QAS_KEY: {
                           f"{TURN_KEY}_0": {
                               QUESTION_KEY: f"{item['instruction']} {DEFAULT_SEGMENT_TOKEN}{INPUT_NAME}: {input_str}" if
                               input_str != "" else f"{item['instruction']}",
                               ANSWER_KEY: item['output']}}
                       }
        fw.write(f"{json.dumps(cur_example)}\n")

print(f"save to:{save_f}")
