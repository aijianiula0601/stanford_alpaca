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
# 去掉原始gpt35中的一些prompt然后再训练
#----------------------------------------------------------

your_random_port=11224

base_dir='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_gpt3.5sex_prompt'
llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft_outs/checkpoint-5000"
output_dir="${base_dir}/ft_out_5000"
data_json="${base_dir}/gpt35sex_prompt.json"

mkdir -p ${output_dir}

torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/mask_header_answer/train_multi_round_mask_answer_multitype_dataset.py \
  --model_name_or_path "${llama_ckpt_and_tokenizer}" \
  --data_path ${data_json} \
  --output_dir ${output_dir} \
  --num_train_epochs 6 \
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
  --fp16 True \
  --process_name 'gpt35_process_prompt'
