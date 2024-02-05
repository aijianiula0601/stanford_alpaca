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
    "current_user_response": "yeah, send me your picture.",
    "language": "english",
}

if __name__ == '__main__':
    gpt_res = get_prompt_result(prompt_file=prompt_file_dic['stage2_know_each_other'], map_dic=map_dic, gpt_version="gpt4")

    print(gpt_res)
