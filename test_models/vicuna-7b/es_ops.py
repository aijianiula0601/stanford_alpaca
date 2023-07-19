import json
from elasticsearch import Elasticsearch

import urllib3

urllib3.disable_warnings()


def insert_example(es, index_name, example, id):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
    res = es.index(index=index_name, body=example, id=id)
    # es.indices.refresh(index=index_name)

    return res


def search_all(es):
    result = es.search(
        index=index_name,
        query={
            "match_all": {}
        }
    )
    return result['hits']['hits']


def get_data_id(es, index_name, id):
    rs = es.get(index=index_name, id=id)
    return rs['_source']


def delete_index(es, index_name):
    rs = es.indices.delete(index=index_name)
    return rs


def index_count(es, index_name):
    res = es.count(index=index_name)
    return res['count']


if __name__ == '__main__':
    es = Elasticsearch("https://202.168.97.165:9200", http_auth=('elastic', 'EwelDkaFv8l_VBYO_UDL'), verify_certs=False)
    index_name = 'qas_data'
    example = {
        "background": "Khamari is worried about his appearance because he wants to look his best for the upcoming dance. He's unsure what to wear and how to style his hair, and he doesn't want to end up looking like a fool.",
        "dataset_name": "sota",
        "human_name": "Khamari",
        "bot_name": "Alex",
        "qas": [
            {
                "question": "Hey, Alex. Do you have a minute?",
                "answer": "Yeah, sure. What's up?"
            },
            {
                "question": "I need some advice. I'm going to the winter dance next week and I want to look my best, but I have no idea what to wear or how to style my hair. Do you think you could help me out?",
                "answer": "Of course! Let's start with what you're going to wear. Have you given any thought to that?"
            },
            {
                "question": "Not really. I was thinking maybe a suit, but I'm not sure if that's too formal.",
                "answer": "A suit can be a good choice, but it might be too hot to wear one dancing all night. Plus, it might be a little too dressy for the dance. Maybe you could try something like a button-down shirt with nice pants or jeans. That would look good and still be comfortable."
            }
        ]

    }

    # print(insert_example(index_name, example, id=1))
    # print(search_all())
    # delete_index(index_name)
    # print(get_data_id(index_name, id=1))
    print(index_count(es, index_name))
