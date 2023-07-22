#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v12"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_path="${base_dir}/train_data_34970648.txt"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}


#----------------------
# dataset
#----------------------

data_len=`echo $(basename ${data_path} .txt)|awk -F '_' '{print $NF}'`

#----------------------
# train
#----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train_big_file.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --cache_dir ${cache_dir} \
    --output_dir ${output_dir} \
    --data_path ${data_path} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 10 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 5000 \
    --model_max_length 2048 \
    --save_total_limit 10 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "vicuna7b-v12_bigfile" \
    --lazy_load \
    --mask_head \
    --mask_question \
    --mask_except_last_answer \
    --data_len ${data_len} \
    --preload_n 5000
