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
# 去掉原始gpt35中的一些prompt然后再训练,第一第二版本加起来约4000个对话
# 处理数据脚本：process_gpt35sexprompt.py
#----------------------------------------------------------

your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitype_data"
llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/falcon-7b"
output_dir="${base_dir}/debug"
data_json="${base_dir}/debug_multi_dataset_qas.json"

mkdir -p ${output_dir}

CUDA_VISIBLE_DEVICES=3 \
torchrun --nproc_per_node=1 --master_port=${your_random_port} test_models/mask_header_answer/train_multi_round_mask_answer_multitype_dataset.py \
  --model_name_or_path "${llama_ckpt_and_tokenizer}" \
  --data_path ${data_json} \
  --output_dir ${output_dir} \
  --num_train_epochs 6 \
  --per_device_train_batch_size 6 \
  --per_device_eval_batch_size 6 \
  --gradient_accumulation_steps 6 \
  --evaluation_strategy "no" \
  --save_strategy "steps" \
  --save_steps 200 \
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
  --fp16 True \
  --process_name 'ft_mutlitype_data'
