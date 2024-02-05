from get_prompts import *


def prompt_test(prompt_file: str, map_dic: dict):
    print("-" * 100)
    print(f"prompt file:{prompt_file}")
    print("-" * 100)
    prompt = _get_prompt_from_md(prompt_file, map_dic)
    message_list = [{"role": 'user', 'content': prompt}]
    re_text = get_gpt35_response(message_list)
    print("re_text:\n", re_text)


def test_end():
    role_name = "sara"
    latest_history = None,
    current_user_question = "hi, are you single?"

    res_text = get_result_from_prompt_end(role_name=role_name, current_user_question=current_user_question, latest_history=latest_history)
    print("【res_text】:\n", res_text)


def test_sex():
    role_name = "sara"
    occupation = "Physician assistant"
    residence = "china"
    hobbies = "Swimming"
    latest_history = None
    user_intention = None
    current_user_question = "hi, i want to sex with you."

    res_text = get_result_from_prompt_sex(role_name=role_name,
                                          occupation=occupation,
                                          residence=residence,
                                          hobbies=hobbies,
                                          latest_history=latest_history,
                                          user_intention=user_intention,
                                          current_user_question=current_user_question)

    print("【res_text】:\n", res_text)


def test_normal():
    role_name = "sara"
    occupation = "Physician assistant"
    residence = "china"
    hobbies = "Swimming"
    latest_history = None
    user_intention = None
    current_user_question = "hi, i want to sex with you."

    res_text = get_result_from_prompt_normal(role_name=role_name,
                                             occupation=occupation,
                                             residence=residence,
                                             hobbies=hobbies,
                                             latest_history=latest_history,
                                             user_intention=user_intention,
                                             current_user_question=current_user_question)

    print("【res_text】:\n", res_text)


def test_whatapp():
    current_user_question = "give me you whatapp number."
    res_text = get_result_from_prompt_whatapp(current_user_question=current_user_question)

    print("【res_text】:\n", res_text)


def test_greeting_first_day():
    role_name = "rosa"
    residence = "china"
    latest_history = (
        "rosa: how are you？😄\n"
        "user: 嗨\n"
        "rosa: 你好，我叫Rosa，做朋友吧！😊\n"
        "user: 嗯嗯\n"
        "rosa: 好无聊，加我吧！😆\n"
        "user: 加什么\n"
        "rosa: 我想找朋友啊，加我呀！\n"

    )
    current_user_question = "额，我意思是加你什么账号?"
    language = "中文"

    res_text = get_result_from_prompt_greeting_first_day(role_name=role_name, residence=residence, latest_history=latest_history, current_user_question=current_user_question, language=language)
    print("【res_text】:\n", res_text)


def test_greeting_second_day():
    role_name = "sara"
    residence = "china"
    yesterday_day_summary = "Yesterday, user discussed travel and hobbies with rosa. user likes swimming and rosa likes yoga. user has been to China's Forbidden City to travel, the most memorable is met in the Forbidden City star Lu Han."
    current_user_question = "hi"
    res_text = get_result_from_prompt_greeting_second_day(role_name=role_name, residence=residence, yesterday_day_summary=yesterday_day_summary, current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_live():
    role_name = "rosa"
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    current_user_question = "yeah"
    res_text = get_result_from_prompt_from_live(role_name=role_name, latest_history=latest_history, current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_live_onshow():
    role_name = "rosa"
    current_user_question = "yeah"
    res_text = get_result_from_prompt_from_live_onshow(role_name=role_name, current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_live_onshow_picture():
    role_name = "rosa"
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    occupation = "Physician assistant"
    residence = "china"
    hobbies = "Swimming"
    current_user_question = "yeah"

    res_text = get_result_from_prompt_from_live_onshow_picture(role_name=role_name, occupation=occupation, residence=residence, hobbies=hobbies, latest_history=latest_history,
                                                               current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_interrupt_to_show():
    role_name = "rosa"
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    current_user_question = "yeah, are you single?"
    res_text = get_result_from_prompt_from_interrupt_chat_to_show(role_name=role_name, latest_history=latest_history, current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_nochat_recommend_to_show():
    role_name = "rosa"
    latest_history = (
        "rosa:  hello, I'm so bored.\n"
        "user:  good\n"
        "rosa:  Saw your profile, wanna be friends? Where are you from ?\n"
        "user:  heaven\n"
        "rosa:  Oh, come on! Where are you really from ?\n"
        "user:  beijing\n"
        "rosa:  Oh, Beijing! That's so cool!\n"
    )
    res_text = get_result_from_prompt_from_nochat_recommend_to_show(role_name=role_name, latest_history=latest_history)
    print("【res_text】:\n", res_text)


def test_chat_analysis():
    role_name = "rosa"
    pic_topics = "selfie,travel",
    story_topics = "occupation,bad_experience_of_today,movie,sports,first_traveling_experience,football_and_dad,childhood,reconcile_with_mom,love_experience,current_relationship_status",
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    current_user_question = "yeah"

    res_text = get_result_from_prompt_chat_analysis(role_name=role_name, latest_history=latest_history, pic_topics=pic_topics, story_topics=story_topics, current_user_question=current_user_question)
    print("【res_text】:\n", res_text)


def test_history_summary():
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    res_text = get_result_from_prompt_history_summary(latest_history=latest_history)
    print("【res_text】:\n", res_text)


def test_history_summary_day():
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    res_text = get_result_from_prompt_history_summary_day(latest_history=latest_history)
    print("【res_text】:\n", res_text)


def test_telling():
    role_name = "rosa"
    latest_history = (
        "rosa: hello, I'm so bored.\n"
        "user:good\n"
        "rosa: Saw your profile, wanna be friends? Where are you from ?\n"
        "user:heaven\n"
        "rosa: Oh, come on! Where are you really from ?\n"
        "user:beijing\n"
        "rosa: Oh, Beijing! That's so cool!\n"
    )
    experience = "I had a boyfriend before, but he had too many girlfriends, and I was insecure and broke up."
    current_user_question = 'Yes. Have you ever been to Beijing?'
    res_text = get_result_from_prompt_telling(role_name=role_name, latest_history=latest_history, experience=experience, current_user_question=current_user_question, language='english')
    print("【res_text】:\n", res_text)


if __name__ == '__main__':
    test_telling()
