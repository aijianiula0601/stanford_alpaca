#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224

base_dir="/data/hjh/tmp"
llama_ckpt_and_tokenizer='eachadea/vicuna-13b-1.1'
output_dir="${base_dir}/ft_out"
data_json="${base_dir}/train_data.txt"
cache_dir="/data/hjh/hugging"

mkdir -p ${output_dir}


##----------------------
## train
##----------------------
CUDA_VISIBLE_DEVICES=4,5,6,7 \
torchrun --nproc_per_node=4 --master_port=${your_random_port} test_models/vicuna-7b/train_mask_control_in_data.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --cache_dir ${cache_dir} \
    --output_dir ${output_dir} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_on_each_node \
    --model_max_length 2048 \
    --save_total_limit 10 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --fp16 True \
    --process_name "vicuna-13b-ft_v2" \
    --lazy_load