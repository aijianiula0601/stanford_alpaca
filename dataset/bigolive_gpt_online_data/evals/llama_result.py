import requests
import json
import random
import orjson

DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_EOS_TOKEN = "</s>"

replace_prompt = "let's play a role game."


def get_prompt_input(post_data: dict):
    role_a = post_data["human_name"]
    role_b = post_data["bot_name"]
    prompt = post_data['prompt']

    qas = post_data['qas']

    history_list = []
    for qa in qas:
        history_list.append(f"{role_a}: {qa['question']}")
        if "answer" in qa:
            history_list.append(f"{role_b}: {qa['answer']}")

    history_str = DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
        [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_b + ":"

    prompt_input = f"{prompt}\n{history_str}"

    return prompt_input


def llama_no_mask_respond(post_data: dict, temperature=0.6, if_self_prompt=False, model_name=None):
    """
    城琦的no_mask模型
    """

    role_a = post_data["human_name"]
    role_b = post_data["bot_name"]
    if if_self_prompt:

        # --------------------------
        # 采用自己的prompt
        # --------------------------
        model_url_dic = {
            "801": "http://202.168.114.99:810/api/llama",
            "802": "http://202.168.114.99:820/api/llama",
        }

        background = post_data["prompt"].replace(replace_prompt, "").strip()
        qas = post_data['qas']

        history_list = []
        for qa in qas:
            cur_qa = [f"{role_a}: {qa['question']}"]
            if "answer" in qa:
                cur_qa.append(f"{role_b}: {qa['answer']}")

            history_list.append(cur_qa)

        request_data = json.dumps({
            "history": [item for item in history_list],
            "temperature": temperature,
            "max_gen_len": 256,
            "background": background,
            "role_a": role_a,
            "role_b": role_b,
        })

        response = requests.post(model_url_dic[model_name], data=request_data)
        json_data = json.loads(response.text)
        text_respond = json_data["result"]
        text_respond = text_respond.strip().split(role_a + ": ")[0]
        return text_respond.strip()
    else:
        # --------------------------
        # 采用gpt线上的prompt
        # --------------------------
        model_url_dic = {
            "801": "http://202.168.114.99:801/api/model",
            "802": "http://202.168.114.99:802/api/model",
        }

        prompt_input = get_prompt_input(post_data)

        request_body = orjson.dumps({
            "prompt": prompt_input,
            "temperature": temperature,
            "max_new_tokens": 256,
            "stop": "###",
            "role_b": role_b,

        })
        response = requests.post(model_url_dic[model_name], data=request_body)

        result = response.json()['result']

        return result


url_f102 = "http://202.168.114.102"
url_v100 = "http://202.168.114.102"

llama_my_model_url = {
    "vicuna-7b_ft_v3": f"{url_f102}:6023/api",
    "vicuna-7b_ft_v4": f"{url_v100}:6024/api",
    "vicuna-7b_ft_v5": f"{url_v100}:6025/api",
    "vicuna-7b_ft_v6": f"{url_f102}:6026/api",
    "llama_multitype_data": f"{url_v100}:5000/api",
    "llama_multitype_data_ft2_v3": f"{url_f102}:5003/api",
    "llama_multitype_data_ft2_v4": f"{url_f102}:5004/api",

}


def my_llama_respond(post_data: dict, temperature=0.6, model_name=None, if_self_prompt=False):
    """
    我自己的模型
    """
    role_a = post_data["human_name"]
    role_b = post_data["bot_name"]
    if if_self_prompt:
        # --------------------------
        # 采用自己的prompt
        # --------------------------
        PROMPT_DICT = {
            # "conversion": (
            #     "{background}\n"
            #     "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Give the state of the action and expressions appropriately. Do not generate identical responses. "
            #     "If the other party proposes to meet, video, phone call, {role_b} should politely reply we can get to know each other better through chatting first.\n"
            #     "{history}"
            # )
            # 去掉动作的
            "conversion": (
                "{background}\n"
                "The following is a conversation with {role_b}. {role_b} should speak in a tone consistent with the identity introduced in the background. Do not generate identical responses. "
                "If the other party proposes to meet, video, phone call, {role_b} should politely reply we can get to know each other better through chatting first.\n"
                "{history}"
            )
        }

        background = post_data["prompt"].replace(replace_prompt, "").strip()

        qas = post_data['qas']
        history_list = []
        for qa in qas:
            history_list.append(f"{role_a}: {qa['question']}")
            if "answer" in qa:
                history_list.append(f"{role_b}: {qa['answer']}")

        message_dic = {"background": background,
                       "role_a": role_a,
                       "role_b": role_b,
                       "history": DEFAULT_SEGMENT_TOKEN + DEFAULT_SEGMENT_TOKEN.join(
                           [item for item in history_list]) + DEFAULT_SEGMENT_TOKEN + role_b + ":"}
        prompt_input = PROMPT_DICT["conversion"].format_map(message_dic)


    else:
        # --------------------------
        # 采用gpt的prompt
        # --------------------------
        prompt_input = get_prompt_input(post_data)

    request_data = json.dumps({
        "prompt_input": prompt_input,
        "temperature": temperature,
        "max_gen_len": 256,
        "role_b": role_b,
        "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(), role_a + ":", DEFAULT_EOS_TOKEN]
    })

    response = requests.post(llama_my_model_url[model_name], data=request_data)

    json_data = json.loads(response.text)
    text_respond = json_data["result"].strip().strip("#").strip()
    return text_respond


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

        # rs = my_llama_respond(post_data, model_name="vicuna-7b", if_self_prompt=True)
        rs = llama_no_mask_respond(post_data, if_self_prompt=True, model_name="802")

        print("-" * 100)
        print(rs)
