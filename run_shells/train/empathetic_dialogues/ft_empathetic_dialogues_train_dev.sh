#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../



#----------------------------------------------------------
# 训练来之 alpaca_cot的数据，共74k
# 得在上一层目录执行：bash /empathetic_dialogues/ft_empathetic_dialogues_train_dev.sh
#----------------------------------------------------------

your_random_port=11225

your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/empathetic_dialogues"
your_output_dir="${base_dir}/ft_output_train_dev"
rm -rf ${your_output_dir}
mkdir -p ${your_output_dir}

train_data_json="${base_dir}/train.json"
eval_data_json="${base_dir}/valid.json"

data_paths="${train_data_json}|${eval_data_json}"

#-----------------
# 根据steps来保存
#-----------------
torchrun --nproc_per_node=8 --master_port=${your_random_port} train_eval.py \
    --model_name_or_path "${your_path_to_hf_converted_llama_ckpt_and_tokenizer}" \
    --data_path ${data_paths} \
    --output_dir ${your_output_dir} \
    --num_train_epochs 10 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 8 \
    --gradient_accumulation_steps 8 \
    --do_eval \
    --evaluation_strategy "steps" \
    --save_strategy "steps" \
    --save_steps 100 \
    --eval_steps 100 \
    --save_total_limit 20 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_strategy "steps" \
    --logging_steps 1 \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed ${curdir}/deepspeed_config.json \
    --fp16 True

