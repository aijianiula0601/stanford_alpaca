import json
import requests

role_b = "Response:"

instruction = "hi, who are you? where are you?"
prompt_input = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:"

model_server_url = "http://202.168.100.165:6020/api"

request_data = json.dumps({
    "prompt_input": prompt_input,
    "temperature": 0.7,
    "role_b": role_b,
    "max_gen_len": 256,
    "stop_words_list": ["###"]
})
response = requests.post(model_server_url, data=request_data)

print(response.text)
