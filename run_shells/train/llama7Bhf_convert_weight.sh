#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../

your_raw_llama_path="/mnt/cephfs/hjh_data/liujunshi_data/llama/"

your_path_to_hf_converted_llama_ckpt_and_tokenizer="./hf7b1_jh"

python3 lib/transformers_jh/src/transformers/models/llama/convert_llama_weights_to_hf.py \
    --input_dir ${your_raw_llama_path} \
    --model_size 7B \
    --output_dir ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}

cp ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}/tokenizer/* ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}/llama-7b/ 