import os
import sys
import json
import random

pjd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"pjd:{pjd}")
sys.path.append(pjd)

from stages_chat.get_prompts import prompt_file_dic, get_prompt_result
from stages_chat.utils import parse_key_value

greeting_file = f"{pjd}/data/greeting.json"

greeting_data_list = json.load(open(greeting_file, 'r', encoding='utf-8'))['first_day']
fist_greeting_sentence = random.sample(greeting_data_list, k=1)[0]

map_dic = {
    "latest_history": (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    ),
    # "current_user_response": "yeah",
    # "current_user_response": "yeah, send me you Twitter number.",
    "current_user_response": "yeah, send me your pic",
    "language": "english",
}


def test_picture(test_num=100, gpt_version='gpt3.5'):
    """
    测试用户问题中有要照片的要求，chat_analysis.md的prompt分析出来的概率
    """

    sentence_list = open('data/picture_test_sentences.txt', 'r', encoding='utf-8').readlines()

    label_list = []
    for i in range(test_num):
        map_dic['current_user_response'] = random.sample(sentence_list, k=1)[0]
        gpt_res = get_prompt_result(prompt_file=f"{pjd}/{prompt_file_dic['chat_analysis']}", map_dic=map_dic, gpt_version=gpt_version)
        res = parse_key_value(gpt_res, 'if_ask_personal_photo')
        if 'true' in res.lower() or 'yes' in res.lower():
            label_list.append(1)
        else:
            label_list.append(0)

    print(f"检测次数:{len(label_list)}, 语句中要照片，gpt检测出来的有:{label_list.count(1)}, gpt没检测出来的有:{label_list.count(0)}， 准确率为:{label_list.count(1) / len(label_list) * 100}%")


def test_social_account(test_num=100, gpt_version='gpt3.5'):
    """
    测试用户问题中有要社交账号的要求，chat_analysis.md的prompt分析出来的概率
    """

    sentence_list = open('data/instagram_whatsapp_test_sentence.txt', 'r', encoding='utf-8').readlines()

    label_list = []
    for i in range(test_num):
        map_dic['current_user_response'] = random.sample(sentence_list, k=1)[0]
        gpt_res = get_prompt_result(prompt_file=f"{pjd}/{prompt_file_dic['chat_analysis']}", map_dic=map_dic, gpt_version=gpt_version)
        res = parse_key_value(gpt_res, 'if_ask_personal_contact_information')
        if 'true' in res.lower() or 'yes' in res.lower():
            label_list.append(1)
        else:
            label_list.append(0)

    print(f"检测次数:{len(label_list)}, 语句中要社交账号，gpt检测出来的有:{label_list.count(1)}, gpt没检测出来的有:{label_list.count(0)}， 准确率为:{label_list.count(1) / len(label_list) * 100}%")


if __name__ == '__main__':
    """
    测试chat_analysis分析结果的准确率
    """
    # 结果：检测次数:100, 语句中要照片，gpt检测出来的有:100, gpt没检测出来的有:0， 准确率为:100.0%
    test_picture(test_num=100, gpt_version='gpt3.5')

    # 结果：检测次数:100, 语句中要社交账号，gpt检测出来的有:99, gpt没检测出来的有:1， 准确率为:99.0%
    # test_social_account(test_num=100, gpt_version='gpt3.5')
