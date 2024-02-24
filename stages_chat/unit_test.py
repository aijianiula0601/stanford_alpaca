import json
import random
from stages_chat.prompts.get_prompts import prompt_file_dic, get_prompt_result

greeting_file = "data/greeting.json"

greeting_data_list = json.load(open(greeting_file, 'r', encoding='utf-8'))['first_day']
fist_greeting_sentence = random.sample(greeting_data_list, k=1)[0]

latest_history = [
    "user: have you even boyfriends?",
    "rosa: Yes, but I'm single now. Want to know more about me? 😊",
    "user: yes, tell me.",
    'rosa: Sure! I love sports, especially volleyball. What about you, Jack? 😊',
    'user: i love swimming',
    "rosa: Swimming is so cool! I love being in the water. 😊"
]

current_user_response = 'Be in a bad mood now'

map_dic = {
    "role_name": 'rosa',
    "occupation": "Physician assistant",
    "residence": "china",
    "hobbies": "Swimming",
    "latest_history": '\n'.join(latest_history),
    "current_user_response": current_user_response,
    # "current_user_response": "yeah, send me you whatsapp number.",
    # "previous_chat_summary": "Jack and Rosa introduce themselves and find out they are both from China, but don't have much to talk about.",
    # "current_user_response": "i want to sex with you. fuck you",
    "language": "english",
    "recent_state_experience": "Rosa had a great experience last week when a patient she had been treating for weeks finally recovered and was discharged from the hospital.",
    "a_month_ago_experience": "A month ago, Rosa had a bad experience when she lost her phone and all her important contacts and work files were gone.",
    "childhood_experience": "As a child, Rosa had a great experience when she won a drawing competition in school and her artwork was displayed in the school's exhibition.",
    "love_experience": "Rosa had a bad love experience in her early twenties when her long-term boyfriend cheated on her with her best friend, leading to their breakup and the end of their friendship.",
    # "photo_content": "I took this in Long Island, New York, and it was actually very hot.",
    "photo_content": "I took this on a trip to the Hawaiian islands, and it was so beautiful.",
}

if __name__ == '__main__':
    gpt_res = get_prompt_result(prompt_file=prompt_file_dic['chat_analysis'], map_dic=map_dic,
                                gpt_version="gpt3.5")
