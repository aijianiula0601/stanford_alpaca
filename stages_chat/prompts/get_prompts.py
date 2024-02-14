import os
import sys
from pathlib import Path
from stages_chat.utils import get_gpt_response

prompt_file_dic = {'chat_analysis': 'prompts/chat_analysis.md',
                   'history_summary': 'prompts/history_summary.md',
                   'role_experience': 'prompts/role_experience.md',
                   'stage3_familiar': 'prompts/stages/stage3_familiar.md',
                   'stage1_greeting': 'prompts/stages/stage1_greeting.md',
                   'stage2_know_each_other': 'prompts/stages/stage2_know_each_other.md',
                   'stage4_hot': 'prompts/stages/stage4_hot.md',
                   'branch_sex': 'prompts/branches/branch_sex.md',
                   'branch_picture': 'prompts/branches/branch_picture.md',
                   'branch_social_account': 'prompts/branches/branch_social_account.md',
                   'branch_friend_live': 'prompts/branches/branch_friend_live.md',
                   'branch_anchor_virtual_id_live': 'prompts/branches/branch_anchor_virtual_id_live.md'}


def get_prompt_result(prompt_file: str, map_dic: dict, gpt_version: str = "gpt35"):
    prompt = _get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]

    print("-" * 100)
    print("【prompt】:\n")
    print(prompt)
    print("-" * 100)

    return get_gpt_response(message_list, gpt_version)


def _print_prompt_file_dic():
    """
    获取所有prompt对应的文件路径
    """
    base_dir = "prompts"
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
    print("----md_file:", md_file)
    return ''.join(open(md_file, 'r', encoding='utf-8').readlines()).format_map(map_dic).strip()


def get_prompt_from_state(state: str, map_dic: dict):
    """
    根据prompt_file获取prompt内容
    Parameters:
        state: 状态
        map_dic: prompt中需要插入的字符串，格式:{'a': '~', 'b': '~'}
    """
    return ''.join(open(f"prompts/stages/{state}.md", 'r', encoding='utf-8').readlines()).format_map(map_dic).strip()


if __name__ == '__main__':
    _print_prompt_file_dic()
