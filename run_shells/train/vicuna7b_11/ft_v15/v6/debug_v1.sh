#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../../



your_random_port=11223

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/v6_v3"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/debug"
data_json="/data/hjh/tmp/train_data.txt"
bigolivedata_colloquial_json="${base_dir}/bigolive_colloquial_turns.txt"
cache_dir="/data/hjh/hugging"

mkdir -p ${output_dir}


#----------------------
# dataset
#----------------------

if [ ! -f "${bigolivedata_colloquial_json}" ]; then

  #口语化数据转为单轮
  org_f="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial.txt"
  python ${curdir}/coloquial2turnqa_v2.py ${org_f} ${bigolivedata_colloquial_json}

fi

if [ ! -f "${data_json}" ]; then
  echo "-------------------------prepare_data-----------------------------------------"
  python ${curdir}/prepare_data_v3.py ${bigolivedata_colloquial_json} ${data_json}
  echo "------------------------------------------------------------------------------"
fi

##----------------------
## train
##----------------------
#CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --nproc_per_node=8 --master_port=${your_random_port} test_models/vicuna-7b/train_mask_control_in_data.py \
    --model_name_or_path "${llama_ckpt_and_tokenizer}" \
    --data_path ${data_json} \
    --cache_dir ${cache_dir} \
    --output_dir ${output_dir} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 6 \
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
    --process_name "vicuna-7b-v15_v6_v3" \
    --lazy_load

