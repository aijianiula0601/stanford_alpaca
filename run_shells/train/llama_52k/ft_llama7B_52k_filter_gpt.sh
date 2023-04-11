#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../

#----------------------------------------------------------
# 在v100中训练，需要去掉：
#   --bf16 True
#   --tf32 True
# 这两个参数，这两个参数是在A100机器上训练的。
#----------------------------------------------------------

train_port=11223
llama_ckpt_and_tokenizer_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k"
output_dir="${base_dir}/llama-7b-hf_train_out_filter_gpt"
data_json="${base_dir}/alpaca_data_cleaned_filter_gpt.json"

torchrun --nproc_per_node=8 --master_port=${train_port} train.py \
  --model_name_or_path "${llama_ckpt_and_tokenizer_dir}" \
  --data_path ${data_json} \
  --output_dir ${output_dir} \
  --num_train_epochs 10 \
  --per_device_train_batch_size 16 \
  --per_device_eval_batch_size 8 \
  --gradient_accumulation_steps 8 \
  --evaluation_strategy "no" \
  --save_strategy "steps" \
  --save_steps 50 \
  --save_total_limit 1000 \
  --learning_rate 2e-5 \
  --weight_decay 0. \
  --warmup_ratio 0.03 \
  --lr_scheduler_type "cosine" \
  --logging_steps 1 \
  --report_to "tensorboard" \
  --gradient_checkpointing True \
  --deepspeed run_shells/train/deepspeed_config.json \
  --fp16 True
