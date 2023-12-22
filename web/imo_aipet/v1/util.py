import openai


def get_gpt4_result(prompt):
    """
    微软的openai账号
    """

    openai.api_type = "azure"
    openai.api_base = "https://gpt4-test-cj-0803.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = 'bca8eef9f9c04c7bb1e573b4353e71ae'


    message_list = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        engine="gpt4-16k",
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content'].strip('"').strip('“').strip('”')


def get_gpt35_result(prompt):
    """
    微软的openai账号
    """

    openai.api_type = "azure"
    openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = "19ea901e8e10475da1bb0537abf8e5a4"


    message_list = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        temperature=0.6,
        messages=message_list
    )
    return response['choices'][0]['message']['content'].strip('"').strip('“').strip('”')
