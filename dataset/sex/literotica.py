import os
import sys
import json
import jsonlines

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/text/sex/Literotica.jsonl"

with open(org_f, "r+", encoding="utf8") as f:
    i = 0
    for item in jsonlines.Reader(f):
        print(json.dumps(item))
        print("-" * 100)
        i += 1
        if i > 10:
            break
