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

your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
your_output_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/debug_output"

rm -rf ${your_output_dir}
mkdir -p ${your_output_dir}

#data_json="./alpaca_data.json"
train_data_json="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/debug_alpaca_data_cleaned.json"
eval_data_json="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/debug_alpaca_data_cleaned.json"

data_json="${train_data_json}|${eval_data_json}"


torchrun --nproc_per_node=1 --master_port=${your_random_port} train_eval.py \
    --model_name_or_path "${your_path_to_hf_converted_llama_ckpt_and_tokenizer}" \
    --data_path "${data_json}" \
    --output_dir ${your_output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 16 \
    --gradient_accumulation_steps 8 \
    --do_eval \
    --evaluation_strategy "epoch" \
    --save_strategy "epoch" \
    --save_total_limit 20 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed ${curdir}/deepspeed_config.json \
    --fp16 True

