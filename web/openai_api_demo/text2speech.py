from pathlib import Path
import openai
import os

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

    base_dir = "/Users/jiahong/Downloads/openai_audios_demo"
    os.system(f"mkdir -p {base_dir}")

    for voice_type in voice_type_list:
        speech_file_path = f"{base_dir}/speech_{voice_type}.mp3"
        prompt = "It's a nice day. Do you have any plans for today?"
        text2speech(prompt, speech_file_path, voice_type)
        print(f"save to:{speech_file_path}")
