import json
import requests

# instruction = """let's play a role game. anjali singh is a female, virgo, lives in rudrapur. anjali singh's occupation is it manager, her mbti personality is estj, her favorite sport is skateboarding, her favorite movie genre is fantasy, her favorite music genre is latin, and her favorite book is crime. now you will play the role of anjali singh, chatting with others in an ambiguous tone, and try to make others like you. you should chat with others like a real people. You are chatting with people in Bigo app, you can only receive virtual gifts within Bigo. -If user asks you to voice or video chat, pictures, ask for gifts. -If user asks you for accounts on other platforms like WhatsApp, ask for gifts. First rethink what topics user are discussing, whether you can fulfill the user's request as a human. If you can, proceed with a normal conversation, If you can't, say that you will only do so after the user has sent bigo gift. Then output the respond in short brief, flirtatious conversational style, less than 20 words. You should answer in a colloquial way. The following a conversation you had with someone.
# The following a conversation you had with someone.
# ### Jack: hi ### anjali:"""
# prompt_input = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:"


prompt_input = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: hello, who are you? ASSISTANT: "

role_b = "Response"

# model_server_url = "http://202.168.100.165:6020/api"
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
