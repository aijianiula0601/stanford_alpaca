# Note: The openai-python library support for Azure OpenAI is in preview.
import os
import openai

# endpoint = https://gpt4-test-cj-0803.openai.azure.com/openai/deployments/gpt4-16k/chat/completions?api-version=2023-03-15-preview
key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

openai.api_type = "azure"
openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'

if __name__ == '__main__':
    chat_str = (
        "Hey Shavon, what's up? You seem troubled.\n"
    )

    message_list = [
        {"role": "system",
         "content": "Modify the following statements to be more colloquial, like friends chatting on whatsapp, colloquial and speaking like a human. If the sentence is emotional, add emojis that match human emotions. Depending on the meaning of the sentence, it is necessary to add emojis only when there is an emotional expression. Be careful not to change the meaning of the sentence while speaking colloquially, don't always speak in a flirty tone, and don't take it upon yourself to add greeting words."},
        {"role": "user", "content": f"{chat_str}"}

    ]

    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        messages=message_list,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    print(response)
    print("-" * 100)
    print(response['choices'][0]['message']['content'])
    print("-" * 100)
