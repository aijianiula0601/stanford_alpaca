import requests
import json
import random
import orjson

DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_EOS_TOKEN = "</s>"


def get_prompt_input(post_data: dict):
    role_a = post_data["human_name"]
    role_b = post_data["bot_name"]
    prompt = post_data['prompt']

    qas = post_data['qas']

    history_list = []
    for qa in qas:
        history_list.append(f"{role_a}: {qa['question']}{DEFAULT_EOS_TOKEN}")
        if "answer" in qa:
            history_list.append(f"{role_b}: {qa['answer']}{DEFAULT_EOS_TOKEN}")

    history_str = DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
        [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_b + ":"

    prompt_input = f"{prompt}\n{history_str}"

    return prompt_input


def llama_no_mask_respond(post_data: dict, temperature=0.6):
    prompt_input = get_prompt_input(post_data)

    urls = [
        "http://202.168.114.99:801/api/model",
        "http://202.168.114.99:802/api/model",
    ]
    url = urls[random.randint(0, len(urls) - 1)]

    # query
    request_body = orjson.dumps({
        "prompt": prompt_input,
        "temperature": temperature,
        "max_new_tokens": 256,
        "stop": "###"
    })
    response = requests.post(url, data=request_body)
    result = response.json()['result']

    return result


llama_my_model_url = {
    "gpt35sex": "http://202.168.100.251:5021/api",
    "mask_head_answer": "http://202.168.100.251:5018/api",
    "gpt35sex_self_prompt": "http://202.168.114.102:6023/api",
    "bigolive_chat": "http://202.168.114.102:6024/api",
    "less_multitype_data": "http://202.168.114.102:6024/api",
}


def my_llama_respond(post_data: dict, temperature=0.6, model_name=None):
    prompt_input = get_prompt_input(post_data)
    role_a = post_data["human_name"]

    request_data = json.dumps({
        "prompt_input": prompt_input,
        "temperature": temperature,
        "max_gen_len": 256,
        "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(), role_a + ":", DEFAULT_EOS_TOKEN]
    })
    response = requests.post(llama_my_model_url[model_name], data=request_data)

    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    return text_respond.replace("#", "").strip()


if __name__ == '__main__':
    if __name__ == '__main__':
        # ------------
        # role_a
        # ------------
        post_data = {
            "prompt": "let's play a role game. joao corredor is a female, libra, lives in santa ana. joao corredor's occupation is loan officer, her mbti personality is enfp, her favorite sport is boxing, her favorite movie genre is indie, her favorite music genre is blues, and her favorite book is psychology. now you will play the role of joao corredor, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people.",
            "human_name": "Kristi Martinez",
            "bot_name": "Joao Corredor",
            "qas": [
                {
                    "question": "Good",
                    "answer": "evening! How are you doing today? It's nice to meet you."
                },
                {
                    "question": "Good. Nice to meet you too",
                    "answer": "That's great! So, what have you been up to lately? Anything interesting happening in your life?"
                },
                {
                    "question": "Not much",
                }]
        }

        rs = my_llama_respond(post_data, model_name="gpt35sex")

        print("-" * 100)
        print(rs)
