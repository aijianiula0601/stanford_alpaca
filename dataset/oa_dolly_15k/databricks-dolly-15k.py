import os
import sys
import jsonlines
import json
from tqdm import tqdm

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pdf}")
sys.path.append(pdf)

from dataset.data_utils import *

# --------------------------------------------------------------------
# 下载地址：https://huggingface.co/datasets/databricks/databricks-dolly-15k/tree/main
# --------------------------------------------------------------------

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/instruction/databricks-dolly-15k"
org_f = f"{base_dir}/databricks-dolly-15k.jsonl"
save_f = f"{base_dir}/prepare2qas_databricks-dolly-15k.json"

qas_data_list = []
with open(org_f, "r+", encoding="utf8") as f:
    for item in tqdm(jsonlines.Reader(f)):

        # 只拿有context内容的数据
        if item['context'].strip() != "":
            cur_example = {DATASET_KEY: DATABRICKS_DOLLY_15K_DATASET_NAME,
                           BACKGROUND_KEY: item["context"],
                           HUMAN_NAME_KEY: HUMAN_DEFAULT_NAME,
                           BOT_NAME_KEY: BOT_DEFAULT_NAME,
                           QAS_KEY: {
                               f"{TURN_KEY}_0": {
                                   QUESTION_KEY: f"{item['instruction']}",
                                   ANSWER_KEY: item['response']}}
                           }
            qas_data_list.append(cur_example)

print(f"all:{len(qas_data_list)}")
check_data_format(qas_data_list)
json.dump(qas_data_list, open(save_f, 'w'))
print(f"save to:{save_f}")
