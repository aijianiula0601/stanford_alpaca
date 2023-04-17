# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "a15cfae7bd4c47d68172e85649653725"

response = openai.ChatCompletion.create(
    engine='bigo-gpt35',
    messages=[
        {"role": "system",
         "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
        {"role": "user", "content": "hi, Kervin"},
        {"role": "assistant", "content": "I am fine, how about you?"},
        {"role": "user", "content": "Where are you?"},
        {"role": "assistant", "content": "I am at home, what about you?"},
        {"role": "user", "content": "Let's go to the library. Will you come with me?"}
    ]
)

print(response)
