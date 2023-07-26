#!/bin/bash

set -ex

curdir=$(pwd)
echo "curdir:$curdir"
cd "$curdir" || exit

CUDA_VISIBLE_DEVICES=0,1 \
gunicorn -c gunicorn_conf.py model_server:app