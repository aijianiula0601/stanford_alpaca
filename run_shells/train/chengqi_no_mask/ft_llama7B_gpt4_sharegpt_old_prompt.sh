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

your_random_port=11226
#your_path_to_hf_converted_llama_ckpt_and_tokenizer="decapoda-research/llama-7b-hf"
#your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/llama-7b-hf"

# your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/finetune_out_gpt4_shared_10_multi/break_check800"
#your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/zhuchengqi/data/aigc/LLM/model_tmp/llama-7b/"
your_path_to_hf_converted_llama_ckpt_and_tokenizer="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/junshi_llama-7b"

# your_path_to_hf_converted_llama_ckpt_and_tokenizer="./trained_models/finetune_out_gpt4_shared/checkpoint-1400"

save_base_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/chengqi_no_mask"

your_output_dir="${save_base_dir}/finetune_out_soda_maskPrompt/"
# your_output_dir="./finetune_out_gpt4_shared_10_multi/"

#程琦目录：/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/gpt4_sodatrain_name.json
#训练目录：/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/run_shells/train sh ft_llama7B_gpt4_sharegpt_old_prompt.sh
data_json="${save_base_dir}/gpt4_sodatrain_name.json"

torchrun --nproc_per_node=8 \
  --master_port=${your_random_port} test_models/chengqi_no_mask/train_multi_round_old_withPrompt.py \
  --model_name_or_path "${your_path_to_hf_converted_llama_ckpt_and_tokenizer}" \
  --data_path ${data_json} \
  --output_dir ${your_output_dir} \
  --num_train_epochs 3 \
  --per_device_train_batch_size 6 \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps 4 \
  --evaluation_strategy "no" \
  --save_strategy "steps" \
  --save_steps 100 \
  --model_max_length 2048 \
  --save_total_limit 100 \
  --learning_rate 2e-5 \
  --weight_decay 0. \
  --warmup_ratio 0.03 \
  --lr_scheduler_type "cosine" \
  --logging_steps 1 \
  --report_to "tensorboard" \
  --gradient_checkpointing True \
  --deepspeed run_shells/train/deepspeed_config.json \
  --fp16 True \
  --lazy_preprocess True
