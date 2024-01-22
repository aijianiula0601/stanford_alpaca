import os
import sys
from pathlib import Path
from utils import get_gpt35_response, get_gpt4_response

pjd_file = os.path.dirname(os.path.abspath(__file__))
print(f"pdf_file:{pjd_file}")
sys.path.append(pjd_file)

prompt_file_dic = {
    'greeting_first_day': 'states/greeting_first_day.md',
    'whatapp': 'states/whatapp.md',
    'en': 'states/end.md',
    'normal': 'states/normal.md',
    'telling': 'states/telling.md'
}


def print_prompt_file_dic():
    """
    获取所有prompt对应的文件路径
    """
    base_dir = "prompts/"
    prompt_file_dic = {}
    for f in Path(base_dir).rglob("*.md"):
        prompt_name = f.name.strip(".md")
        prompt_file_dic[prompt_name] = str(f)

    print("prompt_file_dic:")
    print(prompt_file_dic)
    return prompt_file_dic


def get_prompt_from_md(md_file: str, map_dic: dict):
    """
    根据prompt_file获取prompt内容
    Parameters:
        md_file: 保存prompt的md文件路径
        map_dic: prompt中需要插入的字符串，格式:{'a': '~', 'b': '~'}
    """
    return ''.join(open(md_file, 'r', encoding='utf-8').readlines()).format_map(map_dic)


def prompt_test(prompt_file: str, map_dic: dict):
    print("-" * 100)
    print(f"prompt file:{prompt_file}")
    print("-" * 100)
    prompt = get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]
    re_text = get_gpt35_response(message_list)
    print("re_text:", re_text)


if __name__ == '__main__':
    print_prompt_file_dic()

    map_dic = {
        "current_user_question": "Are you single?"
    }
    md_file = "prompts/states/whatapp.md"
    prompt_test(prompt_file=md_file, map_dic=map_dic)
