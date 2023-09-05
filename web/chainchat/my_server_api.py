import json
import requests
import time
from openai.openai_object import OpenAIObject

url_f102 = "http://202.168.114.102"
model_server_url = f"{url_f102}:61563/api"


def get_my_server_result(messages, temperature=0.9, role_b="user"):
    # messages = [{"role": "user", "content": prompt}]
    prompt_input = f"{messages[0]['content']}"

    request_data = json.dumps({
        "prompt_input": prompt_input,
        "temperature": temperature,
        "role_b": role_b,
        "max_gen_len": 256,
        "stop_words_list": []
    })

    response = requests.post(model_server_url, data=request_data)

    json_data = json.loads(response.text)
    text_respond = json_data["result"]

    res_text = text_respond.replace("#", "").strip()

    if res_text is None:
        return None

    res_dic = {
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": res_text,
                    "role": "assistant"
                }
            }
        ],
        "created": int(time.time()),
        "id": "chatcmpl-7v33VJVlqPeNnZTNL4IE3zbVoFMS4",
        "model": "gpt-4",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": 161,
            "prompt_tokens": 237,
            "total_tokens": 398
        }
    }

    return res_dic


if __name__ == '__main__':
    prompt = "hi"
    messages = [{"role": "user", "content": prompt}]

    res_dic = get_my_server_result(messages, temperature=0.7)

    print(res_dic)
