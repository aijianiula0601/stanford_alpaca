import json
import os
import sys

pfd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(pfd)

from dataset.alpaca_cot.instruction2qas import instruction2example

org_f = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT/xP3/en/merged_en.json"
save_f = "/mnt/cephfs/hjh/common_dataset/nlp/QingyiSi_Alpaca-CoT/Alpaca-CoT/xP3/en/merged_en.txt"

i = 0
with open(save_f, 'w', buffering=1) as fw:
    with open(org_f, 'r') as fr:
        for example in fr:
            clean_example = example.strip().rstrip(",").lstrip("[").rstrip("]")
            qa_example = instruction2example(json.loads(clean_example))
            fw.write(f"{json.dumps(qa_example)}\n")
            i += 1
            if i % 20000 == 0:
                print(i)
print("done!")
