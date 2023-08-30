import json
import random
import sys
from tqdm import tqdm

turns_f = sys.argv[1]
save_sample_turns_f = sys.argv[2]

# -------------------------------
# 对每个topic的数据进行索引
# -------------------------------
topic_names_to_example_dic = {}
with open(turns_f) as fr:
    for line in tqdm(fr.readlines()):
        example = json.loads(line)

        topic = example['qas']['turn_0']['topic']
        if topic not in topic_names_to_example_dic:
            topic_names_to_example_dic[topic] = [example]
        else:
            topic_names_to_example_dic[topic].append(example)

print(f"所以topic到examples完成！topic个数为：{len(topic_names_to_example_dic)}")

# -------------------------------
# 每个topic抽取10个example
# -------------------------------

sample_n = 10
with open(save_sample_turns_f, 'w') as fw:
    for topic in topic_names_to_example_dic:
        print(f"topic:{topic}, example_n:{len(topic_names_to_example_dic[topic])}")
        for example in random.sample(topic_names_to_example_dic[topic],
                                     k=min(sample_n, len(topic_names_to_example_dic[topic]))):
            fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_sample_turns_f}")
