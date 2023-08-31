#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../../

your_random_port=11224

base_dir="/data1/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/topic"
#llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_json="${base_dir}/train_data.txt"
cache_dir="/data2/hjh/hungging"

#llama_ckpt_and_tokenizer="${cache_dir}/models--eachadea--vicuna-7b-1.1/snapshots/9d8eea215e00b388a22e8f050768ea8911d41f1d"
llama_ckpt_and_tokenizer='/data2/hjh/hugging/vicuna-7b-1.1'
mkdir -p ${output_dir}

#----------------------
# dataset
#----------------------


if [ ! -f "${data_json}" ]; then
  echo "-------------------------prepare_data-----------------------------------------"
  org_f='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/topic/train_data.txt'
  cp -rf ${org_f} ${data_json}
  echo "------------------------------------------------------------------------------"
fi

##----------------------
## train
##----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train_mask_control_in_data.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_on_each_node \
    --model_max_length 2048 \
    --save_total_limit 10 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "vicuna-7b-v15_topic" \
    --lazy_load
