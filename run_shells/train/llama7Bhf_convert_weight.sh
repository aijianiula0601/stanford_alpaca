#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../

your_raw_llama_path="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama"
your_path_to_hf_converted_llama_ckpt_and_tokenizer="${your_raw_llama_path}/new_llama_7b"

python lib/transformers/src/transformers/models/llama/convert_llama_weights_to_hf.py \
    --input_dir ${your_raw_llama_path} \
    --model_size 7B \
    --output_dir ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}

#cp ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}/tokenizer/* ${your_path_to_hf_converted_llama_ckpt_and_tokenizer}/llama-7b/