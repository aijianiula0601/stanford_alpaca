# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
# key1: 19ea901e8e10475da1bb0537abf8e5a4
# key2: 548e5c0c2aff453e932948927a27bde6
openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"

# role : system|user|assistant
gpt_config = {'engine': 'gpt-35-turbo',
              'role': 'user',
              }

if __name__ == '__main__':
    chat_str = (
        "Hey Shavon, what's up? You seem troubled.\n"
        "Yeah, I am.I'm just having a hard time and needed someone to talk to.\n"
        "Of course, man.I'm always here for you. What's going on?\n"
        "It's just everything. Work is stressing me out, my relationship is falling apart, and I feel like I'm losing touch with my friends.I don't know what to do.\n"
        "Well, let's start with work then. What's going on there?\n"
        "It's just that everything is so demanding and I can't keep up.I'm constantly behind and it feels like I'm never going to catch up.\n"
        "Okay, that does sound pretty tough.But it sounds like you're doing the best you can under the circumstances. Maybe you just need to cut yourself some slack and focus on one thing at a time. As for your relationship, what's going on there?\n"
        "We're just fighting all the time and it feels like we're growing apart instead of together.I don't know if we can make it through this rough patch.\n"
        "Do you still love her?\n"
        "Yes, I do.But it's just so hard right now.\n"
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
