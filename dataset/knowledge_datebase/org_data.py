import json

org_f = "/Users/jiahong/Downloads/gpt4to_colloquial_topic.txt"

ex_str0 = "let's play a role game."
ex_str1 = "now you will play the role of"


def get_topic2qas_dic(limit_turn_n: int = 6):
    """获取一个topic的qas"""

    topic_qas_dic = {}

    topic_uid_pair_dic = {}

    # 存储格式：{'uid_pair': {'prompt':'~','qas':{'turn_i': {'question': '~', 'answer': '~' }}},... }
    uid_pair2qa_example_dic = {}

    with open(org_f) as fr:
        for line in fr:
            example = json.loads(line)
            del example['background']
            del example['prompt_info']
            if len(example['qas']) < limit_turn_n:
                continue

            uid_pair_i = 0
            for i in range(len(example['qas'])):
                qa = example['qas'][f'turn_{i}']
                topic = qa['topic']
                del qa['history']
                del qa['context_send_to_gpt']
                del qa['colloquial_answer']

                if topic not in topic_qas_dic:
                    topic_qas_dic[topic] = []
                topic_qas_dic[topic].append(
                    {
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'uid_pair': example['uid_pair']
                    }
                )

                qa_example = {
                    "prompt": example["prompt"].replace(ex_str0, "").split(ex_str1)[0].strip(),
                    "qas": {f'turn_{i}': qa}
                }
                cur_uid_pair = f"{example['uid_pair']}#{uid_pair_i}"
                uid_pair2qa_example_dic[cur_uid_pair] = qa_example

                if topic not in topic_uid_pair_dic:
                    topic_uid_pair_dic[topic] = set()
                topic_uid_pair_dic[topic].add(cur_uid_pair)

                uid_pair_i += 1

    return topic_qas_dic, topic_uid_pair_dic, uid_pair2qa_example_dic
