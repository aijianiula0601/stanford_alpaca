import json
import os
import sys
import random

pdj = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from dataset.data_utils import *


# -------------------------------------------------------
# 对于多轮的对话，随机采样一个轮次，最后训练时候是训练最后一个answer
# -------------------------------------------------------

def sample_qas_and_mask(example):
    qas = example[QAS_KEY]
    assert len(qas) > 1, f"error length of qas:{len(qas)}"

    random_turn_i = random.randint(1, len(qas) - 1)
    for i in range(random_turn_i, len(qas)):
        del example[QAS_KEY][f"{TURN_KEY}_{i}"]

    # 用户先提问的，mask除了最后一个answer的所有字符
    if example[MASK_QUESTION_KEY]:
        example[MASK_EXCEPT_LAST_ANSWER] = True
        example[MASK_EXCEPT_LAST_QUESTION_ANSWER] = False
    else:
        # 如果原始的数据不能mask question，那么只能mask最后一个qa前所有字符
        example[MASK_EXCEPT_LAST_ANSWER] = False
        example[MASK_EXCEPT_LAST_QUESTION_ANSWER] = True


if __name__ == '__main__':
    base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v3_v2"
    org_f = f"{base_dir}/train_data.txt"
    save_f = sys.argv[1]

    with open(save_f, 'w', buffering=1) as fw:
        with open(org_f) as fr:
            for line in tqdm(fr.readlines()):
                example = json.loads(line)
                if len(example[QAS_KEY]) > 1:
                    # 随机采样一定轮次
                    sample_qas_and_mask(example)

                fw.write(f"{json.dumps(example)}\n")

    print(f"save to:{save_f}")
