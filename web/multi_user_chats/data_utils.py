import os


# ----------------------------------------
# 组装历史数据，作为传入api格式
# ----------------------------------------
def package_messages(background, history=[], user="role_a"):
    """
    :param background: 人设信息
    :param history: 聊天记录，[
        {
            "role_a":{"name":"role_a","content":"----"},
            "role_b":{"name":"role_b","content":"----"},
         }
        ...
    ]
    :param user: 这次是谁开始问问题了


    示例：
        messages = [
            {'role': 'system', 'content': background},
            {'role': 'user', 'content': '查询今天飞浆航班，帮我订张机票'},
            {'role': 'assistant', 'content': '今天暴雨，所有航班取消了'},
            {'role': 'user', 'content': '那我今天行程是什么？'},
        ]
    """
    messages = [{'role': 'system', 'content': background}]
    user_name = "role_a" if user == "role_a" else "role_b"
    assistant_name = "role_b" if user == "role_a" else "role_a"
    for i, item in enumerate(history):
        messages.append({"user": "user", "context": item[user_name]['content']})
        if i == len(history) - 1:
            assert assistant_name not in item, f"最后一条记录，应该没有{assistant_name}才对！"
        # 最后一次是发问者来问，所以没有回答。
        if i < len(history) - 1:
            messages.append({"user": "assistant", "context": item[assistant_name]['content']})
    return messages, user_name


if __name__ == '__main__':
    background = "Alice is a cheerleader, Kervin is football player in highschool, Alice and Kervin is a couple."
    history = [
        {
            "role_a": {"name": "Kervin", "content": "hi"},
            "role_b": {"name": "role_b", "content": "how do you do?"}
        },
        {
            "role_a": {"name": "Kervin", "content": "hiaa"}
        }
    ]
    messages, user_name = package_messages(background, history, user="role_a")
    print(messages)
    print(user_name)
