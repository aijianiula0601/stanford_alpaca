
## 多轮对话训练说明

目前训练的脚本在run_shells/train下面

```
cd run_shells/train
sh ft_llama7B_gpt4_sharegpt_old.sh
```

train_multi_round.py

train_multi_round_old.py 

这两个文件是训练多轮的main入口，_old结尾是因为目前有两个版本transformer，_old版本对应老版本的transformer多卡性能更好，另外一个版本暂时没用到。


## 多轮对话数据说明

目前训练用到的数据是gpt4_shared_data.json

数据地址: /mnt/cephfs/liujunshi_data/Projects/bigo_stanford_alpaca/datasets/

格式是，一轮对话{'from': 'human', 'value':'xxx'},{'from': 'gpt', 'value':'xxx'},{},{}
```
[
  [{'from': 'human', 'value':'xxx'},{'from': 'gpt', 'value':'xxx'},{},{},...],
  ...
]
```

## 多轮对话推理说明
inference目录下面

inference_human_chat.py 是模型和人交互

inference_self_chat.py 是模型和模型自己交互
