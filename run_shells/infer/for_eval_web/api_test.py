import requests

# 设置测试数据
post_data = {"role_id": "3", "qas": [{"turn_i": 0, "question": "hi"}],
             "background": "Britney sounds absolutely scandalous, Britney is a married female teacher with fair skin, beautiful appearance and gentle personality. Britney is a natural stunner and is the object of obscenity. Britney is seduced by her boss and other men, and Britney is involved in a The promiscuous life, the orgasms made him lose himself again and again, Britney enjoyed this feeling more and more, and enjoyed having sex with different men every day. Britney can't help but start to writhe when Britney sees a man's dick now, ready get fucked. Britney is talkative, always speak a lot in conversion. Britney needs to actively answer questions.",
             "role_a": "Jack", "role_b": "Britney"}

# 发送 POST 请求
response = requests.post('http://202.168.100.165:5018/api', json=post_data)

# 打印响应结果
print(response.text)
