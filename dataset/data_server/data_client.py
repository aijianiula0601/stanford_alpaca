import requests
import json

server_url = "http://202.168.97.165:6100"


def check_data(example):
    try:
        assert "background" in example, "key error:background"
        assert "dataset_name" in example, "key error:dataset_name"
        assert "human_name" in example, "key error:human_name"
        assert "bot_name" in example, "key error:bot_name"
        assert "qas" in example, "key error:qas"
    except Exception as e:
        print(e)
        return False
    return True


def get_example():
    response = requests.get(f"{server_url}/qas_data")
    example = json.loads(response.text)
    check_flag = check_data(example)
    while check_flag is False:
        check_flag = check_data(example)

    return example


def get_data_len():
    response = requests.get(f"{server_url}/data_n")
    rs = json.loads(response.text)
    return rs['data_n']


if __name__ == '__main__':
    print(get_example())
