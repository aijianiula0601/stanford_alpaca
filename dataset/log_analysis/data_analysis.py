import numpy as np
import math
import matplotlib.pyplot as plt

from utils import get_get_dialogue_qas


def get_qa_turn_n_list(all_dqa, limit_turn_n):
    """统计所有对话的聊天轮次"""
    qa_turn_n_list = []

    for dqa in all_dqa:
        if len(dqa) > limit_turn_n:
            qa_turn_n_list.append(len(dqa) / 2)  # 一轮包含一个问题和答案

    return qa_turn_n_list


def show_cdf(qa_turn_n_list):
    # sort data
    x = np.sort(qa_turn_n_list)

    # calculate CDF values
    y = 1. * np.arange(len(qa_turn_n_list)) / (len(qa_turn_n_list) - 1)

    # plot CDF
    plt.plot(x, y)
    plt.xlabel('turns')
    plt.show()


def turns_proportion(limit_turn_n, all_turn_n_list):
    """
    统计占比
    大于limit_turn_n的占比
    """

    # 大于指定轮次的对话个数
    greater_turn_count = 0
    # 小于指定轮次的对话个数
    less_turn_count = 0
    for n in all_turn_n_list:
        # if math.floor(n) == limit_turn_n:
        if n >= limit_turn_n:
            greater_turn_count += 1
        else:
            less_turn_count += 1

    # prob = round(greater_turn_count / len(all_turn_n_list) * 100, 2)  # 占比

    # print(f"共有:{len(all_turn_n_list)}，"
    #       f"大于{limit_turn_n}轮的有:{greater_turn_count},"
    #       f"占比:{prob}%")

    return greater_turn_count, less_turn_count


def data_proportion(all_turn_n_list):
    """各个指标的占比"""

    all_da_n = len(all_turn_n_list)

    greater_tc_1, less_tc_1 = turns_proportion(limit_turn_n=1, all_turn_n_list=qa_turn_n_list)
    greater_tc_10, less_tc_10 = turns_proportion(limit_turn_n=10, all_turn_n_list=qa_turn_n_list)

    print(f"共有:{len(all_turn_n_list)}")
    print(f"有回复:{greater_tc_1},占比:{round(greater_tc_1 / all_da_n * 100, 2)}%")
    print(f"无回复:{less_tc_1},占比:{round(less_tc_1 / all_da_n * 100, 2)}%")

    print(
        f"大于10轮:{greater_tc_10},占比:{round(greater_tc_10 / all_da_n * 100, 2)}%,在有回复中占比:{round(greater_tc_10 / greater_tc_1 * 100, 2)}%")
    print(f"小于10轮的:{less_tc_10},占比:{round(less_tc_10 / all_da_n * 100, 2)}%")
    print(f"小于10轮有回复的:{less_tc_10 - less_tc_1},在有回复中占比:{round((less_tc_10 - less_tc_1) / greater_tc_1 * 100, 2)}%")

    limit_turn_n = 10
    greater_tc_, less_tc_ = turns_proportion(limit_turn_n=limit_turn_n, all_turn_n_list=qa_turn_n_list)
    print(
        f"大于{limit_turn_n}轮:{greater_tc_},占比:{round(greater_tc_ / all_da_n * 100, 2)}%,在有回复中占比:{round(greater_tc_ / greater_tc_1 * 100, 2)}%")


def f1(all_turn_n_list, limit_turn_n):
    all_da_n = len(all_turn_n_list)
    greater_tc_1, less_tc_1 = turns_proportion(limit_turn_n=1, all_turn_n_list=qa_turn_n_list)

    greater_tc_, less_tc_ = turns_proportion(limit_turn_n=limit_turn_n, all_turn_n_list=qa_turn_n_list)

    # 在所有对话中占比 %
    in_all_prob = round(greater_tc_ / all_da_n * 100, 2)
    # 在有回复中占比 %
    in_rep_prob = round(greater_tc_ / greater_tc_1 * 100, 2)

    return in_all_prob, in_rep_prob


if __name__ == '__main__':
    f_gpt4 = '/Users/jiahong/Downloads/bigolive_robot_chat_history.20230917.cot_gpt4.en.txt.1'
    f_gpt35 = '/Users/jiahong/Downloads/bigolive_robot_chat_history.20230917.cot_gpt35.en.txt.1'

    f_list = [f_gpt4, f_gpt35]

    for f in f_list:
        print(f"file:{f}")
        all_dialogue_qa = get_get_dialogue_qas(f)

        qa_turn_n_list = get_qa_turn_n_list(all_dqa=all_dialogue_qa, limit_turn_n=0)

        show_cdf(qa_turn_n_list)
        data_proportion(qa_turn_n_list)
        print("-" * 100)

    # -----------------------------------
    # 对比gpt35和gpt4大于多少轮后的占比
    # -----------------------------------

    gpt4_all_prob_list = []
    gpt4_rep_prob_list = []
    all_dialogue_qa = get_get_dialogue_qas(f_list[0])
    qa_turn_n_list = get_qa_turn_n_list(all_dqa=all_dialogue_qa, limit_turn_n=0)

    # 从多少轮到多少轮
    turn_n_range_list = [i for i in range(10, 100)]

    for i in turn_n_range_list:
        iap, irp = f1(qa_turn_n_list, i)
        gpt4_all_prob_list.append(iap)
        gpt4_rep_prob_list.append(irp)

    gpt35_all_prob_list = []
    gpt35_rep_prob_list = []

    all_dialogue_qa = get_get_dialogue_qas(f_list[1])
    qa_turn_n_list = get_qa_turn_n_list(all_dqa=all_dialogue_qa, limit_turn_n=0)

    for i in turn_n_range_list:
        iap, irp = f1(qa_turn_n_list, i)
        gpt35_all_prob_list.append(iap)
        gpt35_rep_prob_list.append(irp)

    # -----------------
    # 在所有对话中占比
    # -----------------
    x = turn_n_range_list
    y1 = gpt4_all_prob_list  # 第一条曲线
    y2 = gpt35_all_prob_list  # 第二条曲线

    plt.subplot(1, 2, 1)
    plt.plot(x, y1, label='gpt4')
    plt.plot(x, y2, label='gpt35')

    plt.legend()

    # 添加标题和坐标轴标签
    plt.title('gpt4|gpt35')
    plt.xlabel('in_all_turns')
    plt.ylabel('prob')

    # -----------------
    # 在有回复中占比
    # -----------------
    x = turn_n_range_list
    y1 = gpt4_rep_prob_list  # 第一条曲线
    y2 = gpt35_rep_prob_list  # 第二条曲线

    plt.subplot(1, 2, 2)
    plt.plot(x, y1, label='gpt4')
    plt.plot(x, y2, label='gpt35')

    plt.legend()

    # 添加标题和坐标轴标签
    plt.title('gpt4|gpt35')
    plt.xlabel('in_rep_turns')
    plt.ylabel('prob')

    # 显示图形
    plt.show()
