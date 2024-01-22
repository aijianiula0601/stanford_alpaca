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


def get_prompt_result(prompt_file: str, map_dic: dict):
    prompt = get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]
    return get_gpt35_response(message_list)


def test_sex():
    map_dic = {
        "role_name": "sara",
        "occupation": "Physician assistant",
        "residence": "china",
        "hobbies": "Swimming",
        "last_summary": None,
        "latest_history": None,
        "user_intention": None,
        "current_user_question": "hi, i want to sex with you."
    }
    md_file = "prompts/states/sex.md"
    get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def test_whatapp():
    map_dic = {
        "current_user_question": "Are you single?"
    }
    md_file = "prompts/states/whatapp.md"
    get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def test_greeting_first_day():
    map_dic = {
        "role_name": "sara",
        "residence": "china",
        "latest_history": None,
        "current_user_question": "hi"
    }
    md_file = "prompts/states/greeting_first_day.md"
    get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def test_greeting_second_day():
    map_dic = {
        "role_name": "sara",
        "residence": "china",
        "yesterday_day_summary": None,
        "current_user_question": "hi"
    }
    md_file = "prompts/states/greeting_first_day.md"
    get_prompt_result(prompt_file=md_file, map_dic=map_dic)


def test_chat_analysis():
    map_dic = {
        "role_name": "rosa",
        "latest_history": (
            "rosa: hello, I'm so bored.\n"
            "user:good\n"
            "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
            "user:heaven\n"
            "rosa: Oh, come on! Where are you really from ?\n"
            "user:beijing\n"
            "rosa: Oh, Beijing! That's so cool!\n"
        ),
        "pic_topics": "selfie,travel",
        "story_topics": "occupation,bad_experience_of_today,movie,sports,first_traveling_experience,football_and_dad,childhood,reconcile_with_mom,love_experience,current_relationship_status",
        "current_user_response": "yeah"
    }
    md_file = "prompts/chat_analysis.md"
    get_prompt_result(prompt_file=md_file, map_dic=map_dic)


if __name__ == '__main__':
    print_prompt_file_dic()
