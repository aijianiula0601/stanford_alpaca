# 说明

加载vicuna-7b-1.1来训练

地址：https://huggingface.co/eachadea/vicuna-7b-1.1

# 数据集


https://huggingface.co/datasets/Open-Orca/OpenOrca/viewer/Open-Orca--OpenOrca/train?p=1


gpt4+gpt35的数据一共400多万，无法一起训练，所有这里只训练gpt4约99w的数据

# 目的

优化prompt理解能力

# 结果

理解能力有提升，比ft_v5中采用multitype好