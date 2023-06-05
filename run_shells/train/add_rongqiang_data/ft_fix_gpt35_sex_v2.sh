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
#之前的永强的数据中聊天记录存在bug,会突然冒出另外人名，这次修复重新训练，并且加上emoji数据 + 第一批数据
#----------------------------------------------------------

your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/mask_header_answer/fix_gpt3.5databug/v2"
llama_ckpt_and_tokenizer="${base_dir}/llama-7b-hf"
output_dir="${base_dir}/ft_outs"
data_json="${base_dir}/merge_data.json"

mkdir -p ${output_dir}


torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/mask_header_answer/train_multi_round_mask_answer_add_end_token_background.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 6 \
    --gradient_accumulation_steps 6 \
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
    --fp16 True
