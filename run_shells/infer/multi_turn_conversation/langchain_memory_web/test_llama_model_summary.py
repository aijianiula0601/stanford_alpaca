import requests
import json
import os
import sys

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

DEFAULT_SEGMENT_TOKEN = "###"
DEFAULT_EOS_TOKEN = "</s>"


def mask_instruct():
    prompt_input = """
    Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.
    EXAMPLE
    Current summary:
    The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.
    New lines of conversation:
    Human: Why do you think artificial intelligence is a force for good?
    AI: Because artificial intelligence will help humans reach their full potential.
    New summary:
    The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
    END OF EXAMPLE
    Current summary:
    New lines of conversation:
    Human: yes, Are you going on a trip?
    Ai: yes I am
    New summary:
    """


    request_data = json.dumps({
        "prompt_input": prompt_input,
        "temperature": 0.9,
        "max_gen_len": 256,
        "stop_words_list": [DEFAULT_SEGMENT_TOKEN.strip(),  "Human:"]
    })
    response = requests.post("http://127.0.0.1:7000/api", data=request_data)

    json_data = json.loads(response.text)
    text_respond = json_data["result"]
    return text_respond.replace("#", "").strip()


if __name__ == '__main__':
    rs = mask_instruct()
    print(rs)
