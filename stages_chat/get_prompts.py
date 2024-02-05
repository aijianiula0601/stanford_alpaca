import os
import sys
from pathlib import Path
from utils import get_gpt35_response, get_gpt4_response

prompt_file_dic = {
    'chat_analysis': 'prompts/chat_analysis.md',
    'history_summary': 'prompts/history_summary.md',
    'history_summary_day': 'prompts/history_summary_day.md',
    'chat_analysis_simple': 'prompts/chat_analysis_simple.md',
    'live': 'prompts/states/live.md',
    'picture_whatsapp': 'prompts/states/picture_whatsapp.md',
    'live_interruptchat_to_show': 'prompts/states/live_interruptchat_to_show.md',
    'normal_with_analysis': 'prompts/states/normal_with_analysis.md',
    'greeting_first_day': 'prompts/states/greeting_first_day.md',
    'live_onshow': 'prompts/states/live_onshow.md',
    'live_onshow_picture': 'prompts/states/live_onshow_picture.md',
    'en': 'prompts/states/end.md',
    'greeting_second_day': 'prompts/states/greeting_second_day.md',
    'normal': 'prompts/states/normal.md',
    'live_nochat_recommend_to_show': 'prompts/states/live_nochat_recommend_to_show.md',
    'telling': 'prompts/states/telling.md',
    'sex': 'prompts/states/sex.md'
}


def get_prompt_result(prompt_file: str, map_dic: dict, gpt_version: str = "gpt35"):
    prompt = _get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]

    print("-" * 100)
    print("【prompt】:\n")
    print(prompt)
    print("-" * 100)

    if gpt_version == "gpt4":
        return get_gpt4_response(message_list)

    return get_gpt35_response(message_list)


def _print_prompt_file_dic():
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


def _get_prompt_from_md(md_file: str, map_dic: dict):
    """
    根据prompt_file获取prompt内容
    Parameters:
        md_file: 保存prompt的md文件路径
        map_dic: prompt中需要插入的字符串，格式:{'a': '~', 'b': '~'}
    """
    return ''.join(open(md_file, 'r', encoding='utf-8').readlines()).format_map(map_dic).strip()


def get_prompt_from_state(state: str, map_dic: dict):
    """
    根据prompt_file获取prompt内容
    Parameters:
        state: 状态
        map_dic: prompt中需要插入的字符串，格式:{'a': '~', 'b': '~'}
    """
    return ''.join(open(f"prompts/states/{state}.md", 'r', encoding='utf-8').readlines()).format_map(map_dic).strip()


if __name__ == '__main__':
    _print_prompt_file_dic()
