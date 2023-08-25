# 说明

陈江修复旧的prompt调用方式后，采用gpt4改造为口语化进行训练。

# 训练

## v1

训练脚本:ft_vicuna7b_v15_v6.sh

采用口语化方式训，采用的prompt还是没有陈江没修复之前的

## v2

不同 prompt 版本筛选方式：

exp_tag=add_gift_prompt： 有送礼引导的

prompt exp_tag=prompt_optimize： 无送礼引导

这个版本的训练，对话exp_tag=prompt_optimize采用原始的prompt


## v3

v2数据的基础上，添加open-platypus数据


## v4

v2的数据，除了bigolive的数据，其他数据复制一遍