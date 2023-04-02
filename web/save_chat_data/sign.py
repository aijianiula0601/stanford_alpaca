import gradio as gr
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


# 创建 Gradio 的界面
def predict(text):
    # 进行预测
    prediction = "您输入的文本是：{}".format(text)
    # 返回结果
    return prediction


def handle_input_text(input_text):
    # 将输入的文本传递给 Flask 应用程序
    url = "http://localhost:8088/"
    data = {"text": input_text}
    response = requests.post(url, data=data)
    # 返回 Flask 应用程序的响应
    return response.json()["result"]


inputs = gr.inputs.Textbox(lines=5, label="请输入文本")
outputs = gr.outputs.Textbox(label="结果")
interface = gr.Interface(fn=handle_input_text, inputs=inputs, outputs=outputs, title="文本预测")


# 创建 Flask 的路由
@app.route("/", methods=["GET", "POST"])
def handle_request():
    if request.method == "POST":
        text = request.form["text"]
        prediction = predict(text)
        # 返回结果
        return jsonify({"result": prediction})


app.run(debug=True, port=8088)

if __name__ == "__main__":
    # 启动 Gradio 界面
    interface.launch(server_port=8089)
    # 启动 Flask 应用程序
