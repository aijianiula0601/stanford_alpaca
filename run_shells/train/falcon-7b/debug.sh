#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../



your_random_port=11225

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data"
#llama_ckpt_and_tokenizer="tiiuae/falcon-7b"
llama_ckpt_and_tokenizer="tiiuae/falcon-7b-instruct"
output_dir="${base_dir}/debug"
data_json="${base_dir}/debug_multi_dataset_qas_checked_max_token_2048.json"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}

CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=4 --master_port=${your_random_port} test_models/folcon-7b/train.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --cache_dir ${cache_dir} \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 10 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 200 \
    --model_max_length 2048 \
    --save_total_limit 50 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --lazy_load \
    --process_name "f7b"
