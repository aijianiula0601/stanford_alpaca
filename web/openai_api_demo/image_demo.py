from openai import OpenAI

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


api_key = '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'

client = OpenAI(api_key=api_key, organization='org-vZinLD7D6tNWUWeWJJtAUyzD')


def prompt2img(prompt):
    res = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    return res.data[0].url


if __name__ == '__main__':
    img_url = prompt2img(prompt="夕阳下，以小女孩，白皮肤，做在海滩上。")
    print(img_url)
