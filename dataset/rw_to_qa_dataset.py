import json
from pandas import read_parquet
import pyarrow.parquet as pq

# ------------------------------------------------------------
# 把deepspeedExample中的数据集处理为qa格式
# ------------------------------------------------------------


# ------------------------------------------------------------
# Dahoas/rm-static
# url:https://huggingface.co/datasets/Dahoas/rm-static
# ------------------------------------------------------------

HUMAN_NAME = "Human"
ASSISTANT_NAME = "Assistant"

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/rm"

train_f = f"{base_dir}/train-00000-of-00001-2a1df75c6bce91ab.parquet"
test_f = f"{base_dir}/test-00000-of-00001-8c7c51afc6d45980.parquet"

data = pq.read_table(test_f, columns=['prompt', 'response'])
print("data line number:", len(data))

print('-' * 100)
print('-' * 100)
print(data.to_pandas())

all_dialogue_data = []
for i, row in data.to_pandas().iterrows():
    line = row['prompt'].strip() + " " + row['response']


    cur_turns_list = []
    pre_qa = ''
    for d in line.split("\n"):
        if d.strip("\n") == "":
            continue
        if d.startswith(HUMAN_NAME + ":") or d.startswith(ASSISTANT_NAME + ":"):
            if pre_qa == "":
                continue
            # -----------
            # 一个问答
            # -----------
            if pre_qa.startswith(ASSISTANT_NAME + ":"):
                pre_qa_dic = {"from": HUMAN_NAME, "value": pre_qa}
            else:
                pre_qa_dic = {"from": ASSISTANT_NAME, "value": pre_qa}
            cur_turns_list.append(pre_qa_dic)
            pre_qa = d
        else:
            pre_qa += d

    # -----------
    # 最后一个
    # -----------
    if pre_qa.startswith(ASSISTANT_NAME + ":"):
        pre_qa_dic = {"from": HUMAN_NAME, "value": pre_qa}
    else:
        pre_qa_dic = {"from": ASSISTANT_NAME, "value": pre_qa}
    cur_turns_list.append(pre_qa_dic)

    # -----------
    # 对话加入
    # -----------
    print(cur_turns_list)
    if len(cur_turns_list) > 1:
        all_dialogue_data.append(cur_turns_list)
    print("-" * 100)
