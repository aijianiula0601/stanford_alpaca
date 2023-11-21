from openai import OpenAI

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------

#线上demo用
# api_key = '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'
#hjh专属用
api_key = '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'

client = OpenAI(api_key=api_key)


def prompt2img(prompt):
    res = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        style="natural",

    )

    return res.data[0].url


if __name__ == '__main__':
    img_url = prompt2img(prompt="生成唯美卡通风格的图片:湛蓝的湖面上，阳光洒下金色的光芒，远处的山林绿意盎然。一只野鸭在湖面上畅游，留下一串泡沫痕迹。")
    print(img_url)
