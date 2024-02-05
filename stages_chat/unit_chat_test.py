import json

from utils import get_gpt4_response, get_gpt35_response, parse_key_value

prompt_md_file = 'prompts/states/greeting_first_day.md'

role_name = "rosa"
chat_history_list = []
occupation = "Physician assistant"
residence = "china"
hobbies = "Swimming"
language = "english"

while True:
    current_user_question = input("user：")
    prompt = ''.join(open(prompt_md_file, 'r', encoding='utf-8').readlines())
    prompt = prompt.format_map({
        'role_name': role_name,
        'latest_history': '\n'.join(chat_history_list),
        'occupation': occupation,
        'residence': residence,
        'hobbies': hobbies,
        'current_user_question': current_user_question,
        'language': language
    })
    print("-" * 100)
    print(prompt)
    print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    # gpt_result = get_gpt4_response(message_list)
    gpt_result = get_gpt35_response(message_list)
    print("-" * 100)
    print(gpt_result)
    print("-" * 100)
    # bot_answer = parse_key_value(text=gpt_result, key='reply')
    bot_answer = gpt_result
    chat_history_list.append(f"user: {current_user_question}\n{role_name}: {bot_answer}")
