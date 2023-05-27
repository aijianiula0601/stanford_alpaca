import os
import sys
import json
import pandas as pd
from pandas import read_parquet

pdf = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"pdj:{pdf}")
sys.path.append(pdf)

from dataset.data_utils import *

# 下载链接：https://huggingface.co/datasets/cnn_dailymail/tree/refs%2Fconvert%2Fparquet/3.0.0


question = "Summarize the context above."

qas_data_list = []


def f(read_f, save_f):
    df_data = read_parquet(read_f, columns=['article', 'highlights'])
    for index in tqdm(df_data.index):
        article = df_data['article'][index]
        highlights = df_data['highlights'][index]

        cur_example = {DATASET_KEY: CNN_DAILYMAIL_DATASET_NAME,
                       BACKGROUND_KEY: article,
                       HUMAN_NAME_KEY: HUMAN_DEFAULT_NAME,
                       BOT_NAME_KEY: BOT_DEFAULT_NAME,
                       QAS_KEY: {
                           f"{TURN_KEY}_0": {
                               QUESTION_KEY: question,
                               ANSWER_KEY: highlights}}
                       }

        qas_data_list.append(cur_example)

    print(f"all:{len(qas_data_list)}")
    check_data_format(qas_data_list)
    json.dump(qas_data_list, open(save_f, 'w'))
    print(f"save to:{save_f}")


if __name__ == '__main__':
    org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/cnn_dailymail-train-00000-of-00003.parquet"
    save_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00000-of-00003.json"

    f(org_f, save_f)

    org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/cnn_dailymail-train-00001-of-00003.parquet"
    save_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00001-of-00003.json"

    f(org_f, save_f)

    org_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/cnn_dailymail-train-00002-of-00003.parquet"
    save_f = "/mnt/cephfs/hjh/common_dataset/nlp/summary/cnn_dailymail/prepare2qas_cnn_dailymail-train-00002-of-00003.json"

    f(org_f, save_f)
