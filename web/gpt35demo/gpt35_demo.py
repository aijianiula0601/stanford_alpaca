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



if __name__ == '__main__':
    message_list = [
        {"role": "system",
         "content": "Let's play a role game. Alice and Kervin are classmate. You are Kervin. I am Alice."},
        {"role": "user", "content": "hi, Kervin"},
        {"role": "assistant", "content": "I am fine, how about you?"},
        {"role": "user", "content": "Where are you?"},
        {"role": "assistant", "content": "I am at home, what about you?"},
        {"role": "user", "content": "Let's go to the library. Will you come with me?"}
    ]

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=0.6,
        messages=message_list
    )
    print(response)
