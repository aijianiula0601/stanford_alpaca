import openai
from openai import OpenAI
import re

def get_gpt_result(engine_name: str = 'gpt-4', message_list: list = [], api_key='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') -> str:
    api_key = api_key
    client = OpenAI(api_key=api_key, organization='org-vZinLD7D6tNWUWeWJJtAUyzD')

    response = client.chat.completions.create(
        model='gpt-4',
        messages=message_list
    )

    res_text = response.choices[0].message.content
    print("=" * 100)
    print(f"response_text:\n{res_text}")
    print("=" * 100 + "\n\n")
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