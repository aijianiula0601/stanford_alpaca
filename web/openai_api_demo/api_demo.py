from openai import OpenAI

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


api_key = "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"

client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(completion.choices[0].message)
print(completion.choices[0].message.content)
