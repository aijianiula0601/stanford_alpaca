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
        "Christina: Hey there! I'm Christina. It's nice to meet you.\n"
        "Guest: Thank you, Christina. I'm glad to be here. This party is a lot of fun.\n"
        "Christina: I know, right? I was just saying to one of the other guests how much I'm enjoying myself. It's great to have a chance to relax and socialize with everyone.\n"
        "Guest: Absolutely. This party has been a great opportunity to catch up with old friends and make some new ones too. What have you been up to lately?\n"
        "Christina: Well, I just recently finished up my degree in psychology. Now I'm working as a researcher at a local university.\n"
        "Guest: That sounds like an interesting job. What kind of research are you doing?\n"
        "Christina: We're currently looking into the effects of social media on mental health. It's been really interesting so far.\n"
        "Guest: Yeah, I can imagine. I've heard that social media can have a pretty big impact on people, both good and bad.\n"
        "Christina: Exactly. That's what we're trying to figure out. So far, it seems like there can be both positive and negative effects depending on how it's used.\n"
        "Guest: That makes sense. I'm sure your research will be helpful in understanding this complex issue better.\n")

    message_list = [
        {"role": "system",
         "content": "Modify the following conversation to be more colloquial, like friends chatting with each other on whatsapp, colloquial and speaking like people. If the sentence is emotional, add emojis that fit the human mood."},
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
