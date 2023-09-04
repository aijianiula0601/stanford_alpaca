import json


# ------------------------------------------------------------------------
# 目的：评估人员选择topic后，根据对话好坏对聊天对话进行排序，加快评估速度
# 排序思路：
# 好对话的大致场景：
#   1.一个对话的话题个数不宜过多
#   2.话题对应的轮次不宜过少，太少说明针对这个话题讨论不够深入
#   3.应排除对话前面几轮的问候话题，不做计算分数已经
#   4.gpt回复后面经常都是反问的，分数应该降低。（绝大部分都反问，无法作为算法依据）
#   5.出现露馅的对话，直接过滤
#   6.一个对话中，问hobbies出现次数越多，分数越低。
#
#
# ------------------------------------------------------------------------


# qas格式：[{'question':'~','answer':'~','topic':'~'}]

def filter_qas(qas: list):
    """出现露馅的对话，直接过滤"""

    if len(qas) <= 0:
        return None
    filter_flag = False
    filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model",
                        "reason=, msg = {}",
                        "text-based program", "As shown in figure"]
    for qa in qas:
        for fw in filter_word_list:
            if fw.lower() in qa['question'].lower() or fw.lower() in qa['answer'].lower():
                filter_flag = True
                break
        if filter_flag:
            break

    if filter_flag:
        return None
    else:
        return qas


def exclude_greet_turns(qas: list):
    """
    排除问候中的轮次，直接排除前面两轮
    """
    filtered_qas = filter_qas(qas[2:])
    if filtered_qas:
        return qas


def get_hobbies_score(qas: list):
    """
    统计出现类似hobbies的个数，越多，分数越低
    """

    hobbies_keyword_dic = {"hobbies": 0, 'favorite movies': 0}
    for qa in qas:
        answer = qa['answer']
        for hk in hobbies_keyword_dic:
            if hk in answer:
                hobbies_keyword_dic[hk] += 1

    score = 0
    for k in hobbies_keyword_dic:
        kn = hobbies_keyword_dic[k]
        if kn == 0:
            score += 0
        else:
            score += 1 / kn

    return score


def get_topic_score(qas: list):
    """根据topic格式计算得分，一个对话中，topic越多，说明聊天越发散"""

    topic_set = set()
    for qa in qas:
        topic = qa['topic']
        topic_set.add(topic)

    t_n = len(topic_set)
    # 整个对话的topic发散分数
    topic_diverge_score = len(qas) / t_n / len(qas)

    return topic_diverge_score


def get_example_score(example: dict):
    """获取整个对话的得分"""
    qas = []
    for i in range(len(example['qas'])):
        qa = example['qas'][f'turn_{i}']
        qas.append({"question": qa['question'], 'answer': qa['answer'], 'topic': qa['topic']})

    qas = exclude_greet_turns(qas)
    if qas is None:
        return 0

    return get_topic_score(qas) + get_topic_score(qas)


def sore_example_list(example_list: list):
    """对一个list中所有example根据qas排序"""

    idx_score_dic = {}
    for i, example in enumerate(example_list):
        idx_score_dic[i] = get_example_score(example)

    sorted_example_list = []
    for i in sorted(idx_score_dic, reverse=True):
        sorted_example_list.append(example_list[i])

    sorted_ids = list(idx_score_dic.keys())

    return sorted_example_list, sorted_ids


if __name__ == '__main__':
    print()
