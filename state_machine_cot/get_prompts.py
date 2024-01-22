import os
import sys
from pathlib import Path
from utils import get_gpt35_response, get_gpt4_response

prompt_file_dic = {
    'greeting_first_day': 'prompts/states/greeting_first_day.md',
    'whatapp': 'prompts/states/whatapp.md',
    'en': 'prompts/states/end.md',
    'normal': 'prompts/states/normal.md',
    'telling': 'prompts/states/telling.md'
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


def get_prompt_result(prompt_file: str, map_dic: dict, gpt_version: str = "gpt35"):
    prompt = get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]

    if gpt_version == "gpt4":
        return get_gpt4_response(message_list)

    return get_gpt35_response(message_list)


def get_prompt_from_sex(role_name: str,
                        occupation: str,
                        residence: str,
                        hobbies: str,
                        last_summary: str,
                        latest_history: str,
                        user_intention: str,
                        current_user_question: str):
    map_dic = {
        "role_name": role_name,
        "occupation": occupation,
        "residence": residence,
        "hobbies": hobbies,
        "last_summary": last_summary,
        "latest_history": latest_history,
        "user_intention": user_intention,
        "current_user_question": current_user_question
    }
    md_file = "prompts/states/sex.md"
    return get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def get_prompt_from_whatapp(current_user_question: str):
    map_dic = {
        "current_user_question": current_user_question
    }
    md_file = "prompts/states/whatapp.md"
    return get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def get_prompt_from_greeting_first_day(role_name: str,
                                       residence: str,
                                       latest_history: str,
                                       current_user_question: str):
    map_dic = {
        "role_name": role_name,
        "residence": residence,
        "latest_history": latest_history,
        "current_user_question": current_user_question
    }
    md_file = "prompts/states/greeting_first_day.md"
    return get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def get_prompt_from_greeting_second_day(role_name: str,
                                        residence: str,
                                        yesterday_day_summary: str,
                                        current_user_question: str):
    map_dic = {
        "role_name": role_name,
        "residence": residence,
        "yesterday_day_summary": yesterday_day_summary,
        "current_user_question": current_user_question
    }
    md_file = "prompts/states/greeting_first_day.md"
    return get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def get_prompt_from_chat_analysis(role_name: str,
                                  latest_history: str,
                                  pic_topics: str,
                                  story_topics: str,
                                  current_user_question: str):
    map_dic = {
        "role_name": role_name,
        "latest_history": latest_history,
        "pic_topics": pic_topics,
        "story_topics": story_topics,
        "current_user_response": current_user_question
    }
    md_file = "prompts/chat_analysis.md"
    return get_prompt_result(prompt_file=md_file, map_dic=map_dic)


if __name__ == '__main__':
    print_prompt_file_dic()
