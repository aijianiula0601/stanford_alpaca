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

#base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/multitype_data_ft2_soda4w_gpt35sex_biglivechat"
base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitype_data"
llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/llama-7b-hf_trainsformer4.28.1"
output_dir="${base_dir}/debug"
data_json="${base_dir}/debug_multi_dataset_qas.json"
#data_json="${base_dir}/soda4w_gpt35sex_biglivechat.json"


#llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
#cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"


rm -rf ${output_dir}
mkdir -p ${output_dir}

CUDA_VISIBLE_DEVICES=3 \
torchrun --nproc_per_node=1 --master_port=${your_random_port} test_models/mask_header_answer/multitype_dataset_pre_token.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 10 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
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
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "checked_dataset"
