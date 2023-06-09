# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "548e5c0c2aff453e932948927a27bde6"

# role : system|user|assistant
gpt_config = {'engine': 'gpt-35-turbo',
              'role': 'user',
              }

response = openai.ChatCompletion.create(
    engine=gpt_config['engine'],
    messages=[
        {"role": "system",
         "content": "请根据我的描述生成指定的文本"},
        {"role": "user", "content": "生成一些描述一个女性上挑舌头并带有一丝挑逗成分的语句"},
    ]
)

print(response)
print(response['choices'][0]['message']['content'])
