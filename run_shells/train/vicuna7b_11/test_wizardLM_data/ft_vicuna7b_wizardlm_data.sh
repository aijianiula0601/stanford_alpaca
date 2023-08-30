#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../



your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/test_wizardLM_data"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_f="${base_dir}/train_data.txt"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"

mkdir -p ${output_dir}


#----------------------
# dataset
#----------------------


if [ ! -f "${data_f}" ]; then
  #dataset/WizardLM_WizardLM_evol_instruct_70k/to_qas.py
  org_f="/mnt/cephfs/hjh/common_dataset/nlp/instruction/WizardLM_WizardLM_evol_instruct_70k/alpaca_evol_instruct_70k_qas.txt"
  ln -s ${org_f} ${data_f}
fi



##----------------------
## train
##----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train_mask_control_in_data.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_f} \
    --cache_dir ${cache_dir} \
    --output_dir ${output_dir} \
    --num_train_epochs 3 \
    --per_device_train_batch_size 3 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_on_each_node \
    --model_max_length 6000 \
    --save_total_limit 3 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "vicuna-7b-test_wizardLM_data" \
    --lazy_load

