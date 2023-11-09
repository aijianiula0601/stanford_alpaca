# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import random
import json


openai.api_type = "azure"
openai.api_base = "https://bigo-chatgpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "0ea6b47ac9e3423cab22106d4db65d9d"

# role : system|user|assistant
gpt_config = {'engine': 'bigo-gpt35',
              'role': 'user',
              }


def main():
    state_generator = (
        # 正常状态生成器
        "Imagine that you are a writer, and you will make up a story about her various stages from childhood to adulthood based on the following information, which includes four parts: childhood experience, college experience, experience in the past year, and experience in the past month."
        "personality:\n"
        "name: Angelie\n"
        "Zodiac Sign: Aries\n"
        "personality: INFP\n"
        "Occupation: Physician Assistant\n"
        "Residence: Liwa\n"
        "Hobbies: Skateboarding, Rom-com movies, pop music, Comic books.\n"
        "now, write the storier, and list the four parts separately with four lines, and each part should be less than 40 words."
    )
    # .format_map({'order': random.choice(['first', 'second', 'third', 'fourth', 'fifth'])})
    
    message_list = [
        {"role": "user",
         "content": state_generator},
    ]

    print(message_list)

    response = openai.ChatCompletion.create(
        engine=gpt_config['engine'],
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    res = response['choices'][0]['message']['content']
    print(res)

    # res = json.loads(res)

    recent_status = [x.replace('\n', ' ') for x in res.split('\n\n')]

    # # print(state_generator)
    # print("-" * 100)
    print(recent_status)
    # print("-" * 100)


if __name__ == '__main__':
    main()