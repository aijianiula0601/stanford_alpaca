
## 多轮对话训练说明增加了soda数据训练

目前训练的脚本在run_shells/train下面

```
cd run_shells/train
sh ft_llama7B_gpt4_sharegpt_old_prompt.sh
```
使用的是train_multi_round_old_withPrompt.py
相比之前train_multi_round_old.py改动是将对话数据加入到了训练里，并且在对话数据里没有进行mask；
现在训练结果取的是checkpoint-1000


## 多轮对话数据说明

目前训练用到的数据是gpt4_sodatrain_name.json

数据地址: /mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/

格式是，一轮对话{'from': 'human', 'value':'xxx'},{'from': 'gpt', 'value':'xxx'},{},{}
```
[
  [{'from': 'human', 'value':'xxx'},{'from': 'gpt', 'value':'xxx'},{},{},...],
  ...
]
如果是对话数据格式是
[
  [{"narrative": '背景', 'from': 'Tom', 'value':'xxx'},{'from': 'Jack', 'value':'xxx'},{},{},...],
  ...
]
```

## 多轮对话推理说明
inference目录下面

inference_human_chat.py 是模型和人交互

inference_self_chat.py 是模型和模型自己交互
