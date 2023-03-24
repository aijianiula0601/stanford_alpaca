#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../


base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama"


python transformers/models/llama/convert_llama_weights_to_hf.py --input_dir ${base_dir} --model_size 7B --output_dir ${base_dir}/new_llama_7b
