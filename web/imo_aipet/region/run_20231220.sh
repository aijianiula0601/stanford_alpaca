#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit




data_time="20231220"
base_dir="/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/region"

save_dir="${base_dir}/${data_time}"
mkdir -p ${save_dir}



description_prompt_dir="${save_dir}/gen_prompts"

echo "#----------------------------------------"
echo "# 3.生成图片"
echo "#----------------------------------------"
imgs_dir="${save_dir}/journey_imgs"
python -u gen3_coun_imgs.py ${description_prompt_dir} ${imgs_dir}


echo "done!"


