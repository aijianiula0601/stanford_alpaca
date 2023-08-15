import json
import os
import sys
from tqdm import tqdm

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

from dataset.data_utils import *

from dataset.es_server.insert_es_data import *

if __name__ == '__main__':
    index_name = 'qas_data'

    data_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v3_v2/train_data.txt"

    with open(data_f) as fr:
        for line in tqdm(fr.readlines()):
            example = json.loads(line)
            insert_example(index_name, example, id=None)
