import json
from elasticsearch import Elasticsearch
import urllib3

urllib3.disable_warnings()

es = Elasticsearch("https://202.168.97.165:9200", http_auth=('elastic', 's6JnANyNuXa5PCjjU0dB'), verify_certs=False)


def insert_example(index_name, example, id):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    res = es.index(index=index_name, body=example, id=id)
    # es.indices.refresh(index=index_name)

    return res


def search_all():
    result = es.search(
        index=index_name,
        query={
            "match_all": {}
        }
    )
    return result['hits']['hits']


def get_data_id(index_name, id):
    rs = es.get(index=index_name, id=id)
    return rs['_source']


def delete_index(index_name):
    rs = es.indices.delete(index=index_name)
    return rs


def index_count(index_name):
    res = es.count(index=index_name)
    return res['count']


if __name__ == '__main__':
    index_name = 'qas_data'
    example = {
        "background": "Juliano finds Kaneisha unpleasant because Juliano feels like Kaneisha is always trying to invade his personal space and meddle in his business. Juliano has repeatedly asked Kaneisha to give him some space, but Kaneisha seems to either not understand or not care. This often leads to conflict and makes Juliano very uncomfortable.",
        "mask_head": True,
        "mask_question": False,
        "mask_except_last_answer": False,
        "dataset_name": "soda",
        "human_name": "Juliano",
        "bot_name": "Kaneisha",
        "qas": {
            "turn_0": {
                "question": "Hey, Kaneisha. Can I talk to you for a second?",
                "answer": "Of course, Juliano. What's up?"
            },
            "turn_1": {
                "question": "Look, I don't mean to be rude, but I really need some space. You always seem to be trying to invade my personal space and meddle in my business. It's really getting on my nerves.",
                "answer": "Juliano, I'm just trying to be friendly. I don't see what the big deal is."
            },
            "turn_2": {
                "question": "The big deal is that I don't want your friendship! I just want you to leave me alone!",
                "answer": "Fine, if that's what you want. But I don't understand why you're being so hostile about it."
            },
            "turn_3": {
                "question": "I'm not being hostile, I'm just telling you how I feel. And I would appreciate it if you would respect my wishes and give me some space.",
                "answer": "Alright, Juliano. I'll back off. But I still don't understand why you're so upset about this."
            }
        }
    }

    print(insert_example(index_name, example, id=None))
    # print(search_all())
    # delete_index(index_name)
    print(get_data_id(index_name, id=1))
    print(index_count(index_name))
