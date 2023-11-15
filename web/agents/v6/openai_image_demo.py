from openai import OpenAI

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


api_key = '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'

client = OpenAI(api_key=api_key)


def prompt2img(prompt):
    res = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="512x512",
    )

    return res.data[0].url


if __name__ == '__main__':
    img_url = prompt2img(prompt="夕阳下，以小女孩，白皮肤，做在海滩上。")
    print(img_url)
