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
your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat"
your_output_dir="${base_dir}/train_output"
data_json="${base_dir}/prepared_train_personality.json"

torchrun --nproc_per_node=8 --master_port=${your_random_port} \
test_models/persona_chat/train_persona_chat.py \
    --model_name_or_path "${your_path_to_hf_converted_llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${your_output_dir} \
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
    --deepspeed ${curdir}/deepspeed_config.json \
    --fp16 True
