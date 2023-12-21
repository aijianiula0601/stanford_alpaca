#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit




data_time="20231219"
base_dir="/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/region"

save_dir="${base_dir}/${data_time}"
mkdir -p ${save_dir}

echo "#----------------------------------------"
echo "# 1.生成所有国家景点名"
echo "#----------------------------------------"

country_places_dir="${base_dir}/country_places"
#python -u gen1_coun_places.py ${country_places_dir}

echo "#----------------------------------------"
echo "# 2.生成文案和图片prompt"
echo "#----------------------------------------"

description_prompt_dir="${save_dir}/gen_prompts"
#python -u gen2_coun_prompt.py ${country_places_dir} ${description_prompt_dir}

echo "#----------------------------------------"
echo "# 3.生成图片"
echo "#----------------------------------------"
imgs_dir="${save_dir}/journey_imgs"
python -u gen3_coun_imgs.py ${description_prompt_dir} ${imgs_dir}


echo "done!"


