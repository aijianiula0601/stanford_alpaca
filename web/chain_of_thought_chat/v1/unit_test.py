import time

limit_turn_n = 2

a = [1, 2, 3, 4, 5]

# [1,2,3,4]  ---> [3,4]


# [3,4,5,6]  ---> [5,6]


history = []

role_human = "user"
user_question = "hi"


def get_latest_history(history: list):
    to_summary_history = None
    new_summary_flag = False
    if len(history) % limit_turn_n == 0 and len(history) // limit_turn_n > 1:
        if len(history) >= limit_turn_n * 2:
            new_summary_flag = True
            # 给过去做总结的历史
            to_summary_history = history[:-limit_turn_n][-limit_turn_n:]

    if new_summary_flag:
        latest_history = history[-limit_turn_n:]
    else:
        cur_turn_n = limit_turn_n + len(history) % limit_turn_n
        latest_history = history[-cur_turn_n:]

    return to_summary_history, latest_history


# 测试获取历史
for i in range(1, 20):
    history.append([i, None])

    # 意图分析，这部分那一定聊天记录去分析，不用关注历史提取

    # 1. 模型回复，需拿历史聊天记录
    _, latest_history = get_latest_history(history[:-1])
    print("-" * 10, i, '-' * 10)
    print(f"给模型回复用的历史记录:{latest_history}")

    # 2. 加上模型回复，添加到history中
    history[-1][-1] = i

    # 3. 做历史总结
    to_summary_history, _ = get_latest_history(history)
    print("原始:", history)
    print('给模型总结用的历史记录:', to_summary_history)
    print()
