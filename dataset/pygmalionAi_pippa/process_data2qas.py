import json

import jsonlines

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/pygmalionAi_pippa"
file_path = f"{base_dir}/pippa_deduped.jsonl"

i = 0
with open(file_path, "r+", encoding="utf8") as f:
    for item in jsonlines.Reader(f):
        print(item)
        if i > 10:
            break
