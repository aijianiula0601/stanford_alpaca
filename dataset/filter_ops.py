import os

from dataset.data_utils import QUESTION_KEY, ANSWER_KEY

# -----------------------------------
# 清洗数据的操作
# -----------------------------------
limit_chat_n = 220


def repair_punctuation(sentence_str: str):
    """
    修复标点符号前面带有空格的语句，如：
    i am fine thank you , cooking is what i love as a foodie .
    i find good stuff on the side walks . . . save money
    """

    sentence_str = sentence_str. \
        replace(" ?", "?"). \
        replace(" !", "!"). \
        replace(" .", "."). \
        replace("...", " ..."). \
        replace(" ,", ",")

    return sentence_str


def filter_qa(qas: dict):
    """过滤露馅"""
    filter_flag = False
    filter_word_list = ["AI", "Language model", "As AI", "as a Language model", "as Language model",
                        "reason=, msg = {}",
                        "text-based program", "As shown in figure"]
    new_qas = {}
    for turn_i in qas:
        qa = qas[turn_i]
        for fw in filter_word_list:
            if fw.lower() in qa[QUESTION_KEY].lower() or fw.lower() in qa[ANSWER_KEY].lower():
                filter_flag = True
                break
        if filter_flag:
            break

        new_qas[turn_i] = qa

    if len(new_qas) > 0:
        return new_qas
    else:
        return None


def toolong_check(answer):
    """
    超过指定长度检测
    """
    if len(answer) > limit_chat_n:
        return True
    else:
        return False


def filter_specify_chat(answer: str):
    return answer.strip().rstrip(":)").rstrip(" :)")


def limit_question_n(answer: str):
    """
    限制问号出现的次数
    """
    qn = answer.count("?")

    if qn > 1:
        return True

    return False


def check_qa(qa_str):
    if toolong_check(qa_str) or limit_question_n(qa_str):
        return True
    return False


def clear_qa(qa_str):
    qa_str = repair_punctuation(qa_str)
    qa_str = filter_specify_chat(qa_str)

    return qa_str


if __name__ == '__main__':
    # sentence_str = "i am fine thank you , cooking is what i love as a foodie ."
    sentence_str = "i find good stuff on the side walks . . . save money"

    print(repair_punctuation(sentence_str))
