import openai
import re
import openai

openai.api_type = "azure"
openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'


def get_gpt_result(message_list: list) -> str:
    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    res_text = response.choices[0].message.content
    return res_text


def parse_res_text(res_text: str, key: str):
    pattern = r'"{0}"\s*:\s*("[^"]*"|[^",]*)'.format(key)
    # pattern = r'"{0}"：\s*"([^"]*)"'.format(key)

    match = re.search(pattern, res_text)
    if match:
        value = match.group(1)
        return value
    else:
        pattern = r'"{0}"\s*：\s*("[^"]*"|[^",]*)'.format(key)
        match = re.search(pattern, res_text)
        if match:
            value = match.group(1)
            return value
        else:
            return None
