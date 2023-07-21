#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224


parent_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v4"
base_dir="${parent_dir}/v3"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_json="${parent_dir}/cleaned_train_data.json"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}


#----------------------
# dataset
#----------------------
if [ ! -f "${data_json}" ]; then
  python ${curdir}/clean_data/clear_data.py ${parent_dir}
fi

#----------------------
# train
#----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --cache_dir ${cache_dir} \
    --output_dir ${output_dir} \
    --num_train_epochs 2 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 400 \
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
    --process_name "vicuna7b_ft_v4_v3" \
    --lazy_load \
    --mask_head \
    --mask_question

