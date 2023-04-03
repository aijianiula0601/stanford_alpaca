#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../



#----------------------------------------------------------
# 在v100中训练，需要去掉：
#   --bf16 True
#   --tf32 True
# 这两个参数，这两个参数是在A100机器上训练的。
#----------------------------------------------------------

your_random_port=11223
#pretrained_model_output_dir="decapoda-research/llama-7b-hf"
#pretrained_model_output_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/llama-7b-hf"

#pretrained_model_output_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
pretrained_model_output_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/stable_transformer_converted_7B"


base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca"
your_output_dir="${base_dir}/debug_output"

data_json="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/alpaca_data_cleaned.json"


torchrun --nproc_per_node=8 --master_port=${your_random_port} train.py \
    --model_name_or_path "${pretrained_model_output_dir}" \
    --data_path ${data_json} \
    --output_dir ${your_output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 8 \
    --gradient_accumulation_steps 8 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 1000 \
    --save_total_limit 2 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed ${curdir}/deepspeed_config.json \
    --fp16 True

