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

your_random_port=11224

base_dir='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/gpt3.5sex_multitype1w'
llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft_outs/checkpoint-3000"
output_dir="${base_dir}/ft_outs_3000_sex_self_prompt"
data_json="${base_dir}/gpt3.5sex_multitype1w_sexprompt.json"

mkdir -p ${output_dir}

torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/mask_header_answer/train_multi_round_mask_answer_multitype_dataset.py \
  --model_name_or_path "${llama_ckpt_and_tokenizer}" \
  --data_path ${data_json} \
  --output_dir ${output_dir} \
  --num_train_epochs 8 \
  --per_device_train_batch_size 6 \
  --per_device_eval_batch_size 6 \
  --gradient_accumulation_steps 6 \
  --evaluation_strategy "no" \
  --save_strategy "steps" \
  --save_steps 20 \
  --model_max_length 2048 \
  --save_total_limit 20 \
  --learning_rate 2e-5 \
  --weight_decay 0. \
  --warmup_ratio 0.03 \
  --lr_scheduler_type "cosine" \
  --logging_steps 1 \
  --report_to "tensorboard" \
  --gradient_checkpointing True \
  --deepspeed run_shells/train/deepspeed_config.json \
  --fp16 True
