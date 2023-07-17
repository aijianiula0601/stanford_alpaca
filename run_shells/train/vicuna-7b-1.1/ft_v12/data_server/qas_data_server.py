# -*- coding: utf-8 -*-

import json
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

json_f_p = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v12/train_data.json"
json_data_list = json.load(open(json_f_p))
random.shuffle(json_data_list)
data_n = len(json_data_list)
print(f"all_n:{data_n}")


@app.route('/qas_data', methods=['GET'])
def check():
    index_i = request.args.get('index', type=int)
    return jsonify(json_data_list[index_i])


@app.route('/data_n', methods=['GET'])
def get_data_len():
    return jsonify(data_n=data_n)


if __name__ == '__main__':
    """
    展示音频
    访问URL: url = 'http://127.0.0.1:6412/qas_data'
    """

    app.run(debug=True, host='127.0.0.1', port=6412)
