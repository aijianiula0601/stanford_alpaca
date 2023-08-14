#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

cd ../../../../../




base_dir="/tmp"
python ${curdir}/prepare_data.py ${base_dir}
