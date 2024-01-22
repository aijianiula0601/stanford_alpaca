from get_prompts import *


def prompt_test(prompt_file: str, map_dic: dict):
    print("-" * 100)
    print(f"prompt file:{prompt_file}")
    print("-" * 100)
    prompt = get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]
    re_text = get_gpt35_response(message_list)
    print("re_text:\n", re_text)


def test_end():
    map_dic = {
        "role_name": "sara",
        "latest_history": None,
        "current_user_question": "hi, are you single?"
    }
    md_file = "prompts/states/end.md"
    prompt_test(prompt_file=md_file, map_dic=map_dic)


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
    prompt_test(prompt_file=md_file, map_dic=map_dic)


def test_whatapp():
    map_dic = {
        "current_user_question": "Are you single?"
    }
    md_file = "prompts/states/whatapp.md"
    prompt_test(prompt_file=md_file, map_dic=map_dic)


def test_greeting_first_day():
    map_dic = {
        "role_name": "sara",
        "residence": "china",
        "latest_history": None,
        "current_user_question": "hi"
    }
    md_file = "prompts/states/greeting_first_day.md"
    prompt_test(prompt_file=md_file, map_dic=map_dic)


def test_greeting_second_day():
    map_dic = {
        "role_name": "sara",
        "residence": "china",
        "yesterday_day_summary": None,
        "current_user_question": "hi"
    }
    md_file = "prompts/states/greeting_first_day.md"
    prompt_test(prompt_file=md_file, map_dic=map_dic)


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
    prompt_test(prompt_file=md_file, map_dic=map_dic)


if __name__ == '__main__':
    test_end()
