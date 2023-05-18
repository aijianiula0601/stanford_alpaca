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
#your_path_to_hf_converted_llama_ckpt_and_tokenizer="decapoda-research/llama-7b-hf"
#your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/llama-7b-hf"

your_path_to_hf_converted_llama_ckpt_and_tokenizer="./hf7b1/llama-7b/"

your_output_dir="./finetune_out_gpt4_shared/"

#data_json="./alpaca_data.json"
data_json="./gpt4_shared_data.json"


torchrun --nproc_per_node=8 \
    --master_port=${your_random_port} train_multi_round.py  \
    --model_name_or_path "${your_path_to_hf_converted_llama_ckpt_and_tokenizer}" \
    --data_path ${data_json}  \
    --output_dir ${your_output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 200 \
    --save_total_limit 1 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --deepspeed ${curdir}/deepspeed_config.json \
    --fp16 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --lazy_preprocess True 
