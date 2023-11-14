from pathlib import Path
import openai

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


openai.api_key = "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"


def text2speech(prompt, save_file_path):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=prompt
    )
    response.stream_to_file(save_file_path)
    print(f"save to:{save_file_path}")


if __name__ == '__main__':
    speech_file_path = "/Users/jiahong/Downloads/speech.mp3"
    prompt = '哎呀，以前看小说漫画得等啊等，作者花了好几个月、几年的时间才创作出来。我们就只能干等，还得催更，时间感觉超级漫长，有时候等到了结果还不尽如人意。可有了AI，简直是个神器，现在谁都能在超短时间里搞出自己想要的小说内容，而且还是特别独一无二、完全按照个人想法来定制的。太方便了！'
    text2speech(prompt, speech_file_path)
