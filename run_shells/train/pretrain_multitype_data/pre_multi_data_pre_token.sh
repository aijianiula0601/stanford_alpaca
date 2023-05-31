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
# zero2配置参考：https://aitechtogether.com/article/45439.html
#----------------------------------------------------------

your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data"
llama_ckpt_and_tokenizer="${base_dir}/llama-7b-hf"
output_dir="${base_dir}/ft_outs_debug"
data_json="${base_dir}/multi_dataset_qas.json"

torchrun --nproc_per_node=1 --master_port=${your_random_port} test_models/mask_header_answer/multitype_dataset_pre_token.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
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
    --deepspeed `pwd`/run_shells/train/deepspeed_config_zero2.json \
    --fp16 True
