# 说明

加载vicuna-7b-1.1来训练

地址：https://huggingface.co/eachadea/vicuna-7b-1.1

# 数据集

ft biglive线上数据

biglive: /mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/onlive_csv_data/20230530-20230615_qas.json


# 结果

效果不错


- 问题
   
    1.训练的数据是以前没有修复每个question和answer在tokenizer后前面自带id=1的问题

    2.这个数据没有还没有修复露馅问题的，准备重新训练


# 0627重新训练

  修复上面的问题1，问题2不修复，是为了跟ft_v4进行对比
