import requests
import json

# from queue import LifoQueue

server_url = "http://202.168.97.165:6100"


# example_memory_lq = LifoQueue(maxsize=5)  # 后进先出队列


def get_example(index_i):
    response = requests.get(f"{server_url}/qas_data?index={index_i}")

    example = json.loads(response.text)
    return example


def get_data_len():
    response = requests.get(f"{server_url}/data_n")
    rs = json.loads(response.text)
    return rs['data_n']


if __name__ == '__main__':
    print(get_example(5))
