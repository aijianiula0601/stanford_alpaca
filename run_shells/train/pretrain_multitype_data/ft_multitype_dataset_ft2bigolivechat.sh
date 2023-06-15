#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../



#----------------------------------------------------------
# 对标数据集：dataset/prepare_soda4w_gpt35_bigolivechat.py
#----------------------------------------------------------

your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/multitype_data_ft2_soda4w_gpt35sex_biglivechat"
#llama_ckpt_and_tokenizer="${base_dir}/llama-7b-hf"
#第一次训练断了，重新加载
llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft_outs_fix_mask/checkpoint-600"
output_dir="${base_dir}/ft_outs_fix_empty_qa"
data_json="${base_dir}/soda4w_gpt35sex_biglivechat_checked_max_token_2048.json"

mkdir -p ${output_dir}

torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/mask_header_answer/train_multi_round_mask_answer_multitype_dataset.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --output_dir ${output_dir} \
    --num_train_epochs 5 \
    --per_device_train_batch_size 6 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 50 \
    --model_max_length 2048 \
    --save_total_limit 30 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed run_shells/train/deepspeed_config.json \
    --fp16 True \
    --process_name "multitype_ft2_soda4w_gpt35sex_biglivechat_fix_empty_qa" \
    --lazy_load \
    --mask_head \
    --mask_question

