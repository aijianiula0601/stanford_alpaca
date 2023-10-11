#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224


base_dir="/data1/hjh/train_vicuna30b"
llama_ckpt_and_tokenizer='/data2/liujunshi/vicuna-33b-v1.3'
output_dir="${base_dir}/debug"
data_json="/data/hjh/tmp/train_data.txt"

mkdir -p ${output_dir}


python test_models/vicuna-7b/train_mask_control_in_data.py -h

##----------------------
## train
##----------------------
#CUDA_VISIBLE_DEVICES=4,5,6,7 \
#torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train_mask_control_in_data.py \
#    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
#    --data_path ${data_json} \
#    --output_dir ${output_dir} \
#    --num_train_epochs 100 \
#    --per_device_train_batch_size 8 \
#    --per_device_eval_batch_size 1 \
#    --gradient_accumulation_steps 4 \
#    --evaluation_strategy "no" \
#    --save_strategy "epoch" \
#    --save_on_each_node \
#    --model_max_length 2048 \
#    --save_total_limit 10 \
#    --learning_rate 2e-5 \
#    --weight_decay 0. \
#    --warmup_ratio 0.03 \
#    --lr_scheduler_type "cosine" \
#    --logging_steps 1 \
#    --report_to "tensorboard" \
#    --gradient_checkpointing True \
#    --deepspeed run_shells/train/deepspeed_config.json \
#    --fp16 True \
#    --process_name "vicuna-30b-ft_v1" \
#    --lazy_load