#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../../

your_random_port=11224

base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/vicuna-7b/ft2_v15/topic"
llama_ckpt_and_tokenizer="eachadea/vicuna-7b-1.1"
output_dir="${base_dir}/ft_out"
data_json="${base_dir}/train_data.txt"
bigolivedata_colloquial_f="${base_dir}/bigolive_colloquial_turns.txt"
cache_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging"
save_f_topic_names_f="${base_dir}/all_topic_names.json"
turns_sample_f="${base_dir}/turns_sample.txt"
mkdir -p ${output_dir}

#----------------------
# dataset
#----------------------

if [ ! -f "${bigolivedata_colloquial_f}" ]; then

  #口语化数据转为单轮
  org_f='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial_topic.txt'
  python ${curdir}/coloquial2turnqa_v2.py ${org_f} ${bigolivedata_colloquial_f} ${save_f_topic_names_f}


fi

if [ ! -f "${turns_sample_f}" ]; then

  #对每个topic数据进行抽样
  python ${curdir}/topic_data_sample.py ${bigolivedata_colloquial_f} ${turns_sample_f}

fi


if [ ! -f "${data_json}" ]; then
  echo "-------------------------prepare_data-----------------------------------------"
  python ${curdir}/prepare_data_v3.py ${turns_sample_f} ${data_json}
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
    --process_name "vicuna-7b-v15_topic" \
    --lazy_load
