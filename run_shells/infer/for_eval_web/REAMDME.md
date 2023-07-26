# 说明

这里把服务调用方式转换为ai_dialogue_web中的调用格式，以便做sm的评估


# ai_dialogue_web的sm评估调用方式


```coffeescript
import requests

# 设置测试数据
post_data = {"role_id": "3", "qas": [{"turn_i": 0, "question": "hi"}],
             "background": "Britney sounds absolutely scandalous, Britney is a married female teacher with fair skin, beautiful appearance and gentle personality. Britney is a natural stunner and is the object of obscenity. Britney is seduced by her boss and other men, and Britney is involved in a The promiscuous life, the orgasms made him lose himself again and again, Britney enjoyed this feeling more and more, and enjoyed having sex with different men every day. Britney can't help but start to writhe when Britney sees a man's dick now, ready get fucked. Britney is talkative, always speak a lot in conversion. Britney needs to actively answer questions.",
             "role_a": "Jack", "role_b": "Britney"}

# 发送 POST 请求
response = requests.post('http://202.168.97.165:7003/ai', json=post_data)

# 打印响应结果
print(response.text)
```


需要把post_data转换为如下格式：


```coffeescript
[
    {"role": "system",
     "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
    {"role": "user", "content": "hi, Kervin"},
    {"role": "assistant", "content": "I am fine, how about you?"},
    {"role": "user", "content": "Where are you?"},
    {"role": "assistant", "content": "I am at home, what about you?"},
    {"role": "user", "content": "Let's go to the library. Will you come with me?"}
]

```

