#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit




#path_to_step_1_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/7B"
path_to_step_1_dir="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/llama-7b-hf_trainsformer4.28.1"
path_to_step_2_dir='/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging/models--WizardLM--WizardCoder-Python-7B-V1.0/snapshots/af130aae779fec3da4ec80bd6a00d03baf4820ac'
path_to_store_recovered_weights="/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/hungging/models--WizardLM--WizardCoder-Python-7B-V1.0_add_llama"

python weight_diff_wizard.py recover --path_raw ${path_to_step_1_dir} --path_diff ${path_to_step_2_dir} --path_tuned ${path_to_store_recovered_weights}