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

training_random_port=11226

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multi_turns_conversation_nomask"
org_model_dir="${base_dir}/llama-7b/"
output_dir="${base_dir}/ft_out_nomask"
data_json="${base_dir}/multi_dataset_qas.json"

torchrun --nproc_per_node=8 --master_port=${training_random_port} test_models/multi_turns_conversation_nomask/train_multi_round_old_withPrompt.py  \
    --model_name_or_path "${org_model_dir}" \
    --data_path ${data_json}  \
    --output_dir ${output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 200 \
    --save_total_limit 10 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --lazy_preprocess True 
