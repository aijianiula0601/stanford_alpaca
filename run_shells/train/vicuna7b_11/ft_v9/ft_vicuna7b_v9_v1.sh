#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../


#只训练一个epoch，防止过拟合。


your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v9/v1"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_json="${base_dir}/train_data.json"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}

#----------------------
# dataset
#----------------------

if [ ! -f "${data_json}" ]; then
  echo "-------------------------prepare_data-----------------------------------------"
  org_f='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v9/train_data.json'
  ln -s ${org_f} ${data_json}
  echo "------------------------------------------------------------------------------"
fi


#----------------------
# train
#----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --cache_dir ${cache_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 19 \
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
    --process_name "vicuna-7b-v9_v1" \
    --lazy_load \
    --mask_head

