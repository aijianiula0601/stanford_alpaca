import gradio as gr
import json
import requests
from flask import session
from gradio.exceptions import Error

from sign_web import USERNAME_KEY, LOGIN_KEY


# 创建 Gradio 的界面
def predict(text):
    # 进行预测
    prediction = "您输入的文本是：{}".format(text)
    # 返回结果
    return prediction


def handle_input_text(input_text):
    # 将输入的文本传递给 Flask 应用程序
    url = "http://localhost:5000/check_login"
    response = requests.get(url)

    username = session[USERNAME_KEY]

    rs_json = json.loads(response.text)
    logged_in = rs_json[LOGIN_KEY]

    if logged_in:
        return f"logged_in:{logged_in},username:{rs_json[USERNAME_KEY]}"

    return f"logged_in:{logged_in}"


gr.Markdown(f"# 欢迎")

inputs = gr.inputs.Textbox(lines=5, label="请输入文本")
outputs = gr.inputs.Textbox(lines=5, label="显示")

interface = gr.Interface(fn=handle_input_text, inputs=inputs, outputs=outputs, title=f"测试",
                         show_error=True)

# 启动 Gradio 界面
interface.launch(server_port=8089)
