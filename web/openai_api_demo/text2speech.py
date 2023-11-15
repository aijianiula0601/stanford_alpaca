from pathlib import Path
import openai

# -----------------------------------------------------------------------------
# 调用方式参考：https://platform.openai.com/docs/api-reference?lang=python
# -----------------------------------------------------------------------------


openai.api_key = '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'



def text2speech(prompt, save_file_path, voice_type: str = 'alloy'):
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice_type,
        input=prompt
    )
    response.stream_to_file(save_file_path)
    print(f"save to:{save_file_path}")


if __name__ == '__main__':
    voice_type_list = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    for voice_type in voice_type_list:
        speech_file_path = f"/Users/jiahong/Downloads/speech_{voice_type}.mp3"
        prompt = '哎呀，以前看小说漫画得等啊等，作者花了好几个月、几年的时间才创作出来。'
        text2speech(prompt, speech_file_path, voice_type)
        print(f"save to:{speech_file_path}")
