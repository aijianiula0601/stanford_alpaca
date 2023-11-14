from openai import OpenAI

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


api_key = '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'

client = OpenAI(api_key=api_key)


# def prompt2img(prompt):
#     res = client.images.generate(
#         model="dall-e-3",
#         prompt=prompt,
#         n=1,
#         size="1024x1024"
#     )
#
#     return res.data[0].url

def prompt2img(prompt):
    res = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="512x512",
    )
    return res.data[0].url


if __name__ == '__main__':
    # img_url = prompt2img(prompt="夕阳下，以小女孩，白皮肤，做在海滩上。")
    img_url = prompt2img(prompt="兔子宠物来到滇池，湖面湛蓝，四周空阔。远处山林茂密，郁郁葱葱。气氛宁静美好。")

    print(img_url)
