import openai

openai_api_key = "548e5c0c2aff453e932948927a27bde6"
openai.api_key = openai_api_key
openai.api_type = "azure"
# openai.api_version = "2023-06-15-preview"
openai.api_version = "2023-03-15-preview"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    if not text:
        text = "this is blank"

    return openai.Embedding.create(
        input=[text], deployment_id=model)['data'][0]['embedding']


if __name__ == '__main__':
    text = "hi"

    print(get_embedding(text))
