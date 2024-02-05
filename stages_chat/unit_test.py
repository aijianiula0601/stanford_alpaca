from get_prompts import prompt_file_dic, get_prompt_result

map_dic = {
    "role_name": 'rosa',
    "occupation": "Physician assistant",
    "residence": "china",
    "hobbies": "Swimming",
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
    "user_intention": None,
    "current_user_response": "yeah",
    "language": "english",
}

if __name__ == '__main__':
    gpt_res = get_prompt_result(prompt_file=prompt_file_dic['greeting_first_day'], map_dic=map_dic, gpt_version="gpt35")

    print(gpt_res)
