import os


# -----------------------------------
# 清洗数据的操作
# -----------------------------------


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


if __name__ == '__main__':
    # sentence_str = "i am fine thank you , cooking is what i love as a foodie ."
    sentence_str = "i find good stuff on the side walks . . . save money"

    print(repair_punctuation(sentence_str))
