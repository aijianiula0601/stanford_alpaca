import json
import random
from utils import get_gpt_response, parse_key_value, response_post_process

role_name = "rosa"
occupation = "Physician assistant"
residence = "china"
hobbies = "Swimming"
language = "english"

greeting_file = "data/greeting.json"

greeting_data_list = json.load(open(greeting_file, 'r', encoding='utf-8'))['first_day']
fist_greeting_sentence = random.sample(greeting_data_list, k=1)[0]
chat_history_list = [f"{role_name}: {fist_greeting_sentence}"]

print(f"{role_name}: {fist_greeting_sentence}")

turn_i = 0
while True:
    current_user_response = input("user：")
    turn_i += 1

    print("=" * 5)
    print("turn_i:", turn_i)
    print("=" * 5)

    prompt_md_file = 'prompts/states/stage2_know_each_other.md'

    prompt = ''.join(open(prompt_md_file, 'r', encoding='utf-8').readlines())
    prompt = prompt.format_map({
        'role_name': role_name,
        'latest_history': '\n'.join(chat_history_list),
        'occupation': occupation,
        'residence': residence,
        'hobbies': hobbies,
        'current_user_response': current_user_response,
        'language': language,
        'recent_state_experience': 'Rosa had a great experience last week when a patient she had been treating for weeks finally recovered and was discharged from the hospital.'
    })
    print("-" * 100)
    print(prompt)
    print("-" * 100)
    message_list = [{"role": "user", "content": prompt}]
    gpt_result = get_gpt_response(message_list, gpt_version='gpt3.5')
    print("-" * 100)
    print(gpt_result)
    print("-" * 100)

    bot_answer = gpt_result

    # bot_answer = response_post_process(bot_answer)
    bot_answer = parse_key_value(text=gpt_result, key='reply')
    chat_history_list.append(f"user: {current_user_response}\n{role_name}: {bot_answer}")
