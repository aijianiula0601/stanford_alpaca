import json

from utils import get_gpt_response, parse_key_value, response_post_process

role_name = "rosa"
occupation = "Physician assistant"
residence = "china"
hobbies = "Swimming"
language = "english"

chat_history_list = []
turn_i = 0
while True:
    current_user_response = input("user：")
    turn_i += 1

    print("=" * 5)
    print("turn_i:", turn_i)
    print("=" * 5)

    if turn_i <= 4:
        prompt_md_file = 'prompts/states/stage1_greeting.md'
        print(f"======md_file:{prompt_md_file}")
    elif turn_i > 4:
        prompt_md_file = 'prompts/states/stage2_know_each_other.md'
        print(f"======md_file:{prompt_md_file}")
    else:
        raise FileNotFoundError

    prompt = ''.join(open(prompt_md_file, 'r', encoding='utf-8').readlines())
    prompt = prompt.format_map({
        'role_name': role_name,
        'latest_history': '\n'.join(chat_history_list),
        'occupation': occupation,
        'residence': residence,
        'hobbies': hobbies,
        'current_user_response': current_user_response,
        'language': language
    })
    print("-" * 100)
    print(prompt)
    print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    gpt_result = get_gpt_response(message_list, gpt_version='gpt3.5')
    print("-" * 100)
    print(gpt_result)
    print("-" * 100)

    if turn_i <= 4:
        bot_answer = gpt_result
    else:
        bot_answer = parse_key_value(text=gpt_result, key='reply')

    bot_answer = response_post_process(bot_answer)
    chat_history_list.append(f"user: {current_user_response}\n{role_name}: {bot_answer}")
