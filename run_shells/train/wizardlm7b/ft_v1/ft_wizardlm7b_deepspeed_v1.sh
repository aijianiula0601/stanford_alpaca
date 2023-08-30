#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224


base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/wizardlm7b/ft_v1"
llama_ckpt_and_tokenizer='WizardLM/WizardCoder-Python-7B-V1.0'
output_dir="${base_dir}/ft_out"
data_json="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v6_v3/train_data.txt"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}


##----------------------
## train
##----------------------
#CUDA_VISIBLE_DEVICES=4,5,6,7 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/llama2/train_mask_control_in_data.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --cache_dir ${cache_dir} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 8 \
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
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "wizardlm-7b-ft_v1" \
    --lazy_load