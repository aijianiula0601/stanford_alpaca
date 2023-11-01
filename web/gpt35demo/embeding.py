import openai

openai_api_key = "548e5c0c2aff453e932948927a27bde6"
openai.api_key = openai_api_key
openai.api_type = "azure"
# openai.api_version = "2023-06-15-preview"
openai.api_version = "2023-03-15-preview"
openai.api_base = "https://bigo-chatgpt-9.openai.azure.com/"

text = "hello"
res = openai.Embedding.create(
    input=[text], deployment_id="text-embedding-ada-002")['data'][0]['embedding']

print(res)
