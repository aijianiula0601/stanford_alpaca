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
    chat_str = (
        "Hey Shavon, what's up? You seem troubled.\n"
        "Yeah, I am.I'm just having a hard time and needed someone to talk to.\n"
    )

    message_list = [
        {"role": "system",
         "content": "Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. If the sentence is emotional, add emojis that match human emotions. Depending on the meaning of the sentence, it is necessary to add emojis only when there is an emotional expression. Be careful not to change the meaning of the sentence while speaking colloquially, don't always speak in a flirty tone, and don't take it upon yourself to add greeting words."},
        {"role": "user", "content": f"{chat_str}"}

    ]


    print(message_list)

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        temperature=0.6,
        messages=message_list
    )
    print(response)
    print("-" * 100)
    print(response['choices'][0]['message']['content'])
    print("-" * 100)
