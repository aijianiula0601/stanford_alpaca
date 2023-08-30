import json
import requests

prompt_input = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: hello, who are you? ASSISTANT: "

role_b = "ASSISTANT:"

model_server_url = "http://202.168.100.165:6013/api"

request_data = json.dumps({
    "prompt_input": prompt_input,
    "temperature": 0.7,
    "role_b": role_b,
    "max_gen_len": 256,
    "stop_words_list": ["###"]
})
response = requests.post(model_server_url, data=request_data)

print(response.text)
