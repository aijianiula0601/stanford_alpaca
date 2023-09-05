import json

# -----------------------------
# 获取一个topic的所有问题和答案
# -----------------------------


from org_data import get_topic2qas_dic


def get_topic_qas(topic: str, topic_qas_dic: dict):
    return topic_qas_dic[topic]


if __name__ == '__main__':

    topic_qas_dic = get_topic2qas_dic(limit_turn_n=6)

    specify_topic = "hobby_food"
    qas, _, _ = get_topic_qas(specify_topic, topic_qas_dic)

    for qa in qas:
        print("question:", qa['question'])
        print("answer:", qa['answer'])
        print()
        print("-" * 20)
