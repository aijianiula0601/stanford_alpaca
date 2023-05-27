import os
import sys
import json
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pdf}")
sys.path.append(pdf)

from dataset.data_utils import *

# 下载地址：https://raw.githubusercontent.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM/main/data/unnatural_instruction_gpt4_data.json
# 说明：该数据集是问一些比较难的问题来让gpt4回答。


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


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/unnatural_instruction_gpt4"
org_f = f"{base_dir}/unnatural_instruction_gpt4_data.json"
save_f = f"{base_dir}/prepare2qas_unnatural_instruction_gpt4_data.json"

org_data = json.load(open(org_f))

qas_data_list = []
for item in tqdm(org_data):
    cur_example = {DATASET_KEY: ALPACA_GPT4,
                   BACKGROUND_KEY: item["input"],
                   HUMAN_NAME_KEY: INSTRUCTION_NAME,
                   BOT_NAME_KEY: RESPONSE_NAME,
                   QAS_KEY: {
                       f"{TURN_KEY}_0": {
                           QUESTION_KEY: f"{item['instruction']} {DEFAULT_SEGMENT_TOKEN}{INPUT_NAME}: {item['label']}" if
                           item["input"].strip() != "" else f"{item['instruction']}",
                           ANSWER_KEY: item['label']}}
                   }
    qas_data_list.append(cur_example)

print(f"all:{len(qas_data_list)}")
check_data_format(qas_data_list)
json.dump(qas_data_list, open(save_f, 'w'))
print(f"save to:{save_f}")
