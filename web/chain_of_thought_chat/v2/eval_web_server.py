import flask
import openai
import json
import random
from flask import Flask, request, jsonify

from chat_web import chat_f

app = Flask(__name__)


def get_history(post_data: dict):
    """转换为gradio中的chatbot的history格式"""
    history_list = []
    last_question = None
    for i, qa in enumerate(post_data['qas']):
        assert qa['turn_i'] == i
        if 'question' in qa and 'answer' in qa:
            history_list.append([qa['question'], qa['answer']])

        if 'question' in qa and 'answer' not in qa and i == len(post_data['qas']):
            last_question = qa['question']

    assert len(history_list) > 0, f"history list less than 1, now is:{len(history_list)}"

    assert last_question is not None, "not question!!!"

    return history_list, last_question


@app.route('/api', methods=['POST'])
def api_server():
    """
    post_data格式：
    {
        "role_id": "3",
        "background": "~",
        "role_a": "User", "role_b": "Britney",
        "qas": [{"turn_i": 0, "question": "hi"}],
    }
    """
    # 返回一个 JSON 响应，其中包含成功添加的数据
    web_post_data = json.loads(request.data)
    # ---------------------------------------------------
    # web传过来的数据转换适当的格式
    # ---------------------------------------------------
    try:
        history, user_question = get_history(post_data=web_post_data)
        role_human = web_post_data['role_a']
        role_robot = web_post_data['role_b']
        last_summary = web_post_data['last_summary']
        gpt_version = web_post_data.get('gpt_version', 'gpt3.5')

        res_history, _, _, history_summary = chat_f(history=history, user_question=user_question,
                                                    last_summary=last_summary,
                                                    role_human=role_human,
                                                    role_robot=role_robot,
                                                    limit_turn_n=5,
                                                    gpt_version=gpt_version)

        res_answer = res_history[-1][-1]

        res_text = res_answer
        print("-" * 100)
        print(f"response:{res_text}")
        print("-" * 100)
        return res_text
    except Exception as e:
        print("-" * 100)
        print(e)
        print("-" * 100)
        return "Service error!"


if __name__ == '__main__':
    app.run(debug=True, port=5019)
