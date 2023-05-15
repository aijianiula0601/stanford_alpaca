# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

# 庞永强账号
openai.api_key = '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'

response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
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
