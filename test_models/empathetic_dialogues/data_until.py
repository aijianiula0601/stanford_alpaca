import json

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"
background_prompt_dic = {
    "history_instruction": (
        "Let's have an open conversation. Below is a history of the question and answer:\n"
        "{history}\n"
        "Please respond according to the question.\n"
    ),
    "no_history_instruction": (
        "Let's have an open conversation. Please respond according to the question\n"
    )
}

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n Question: {question}\n Answer: "
    ),

}


def qas_to_history_str(qas_list):
    qas_str = []
    for qa in qas_list:
        question = qa['question']
        answer = qa['answer']

        qas_str.append(f"Question: {question}\nAnswer: {answer}")

    return "\n".join(qas_str)


def get_prompt_input(example):
    history_len = len(example['qas']) - 1
    if history_len > 0:
        cut_qas = example['qas'][:history_len]
        qa_str = qas_to_history_str(cut_qas)
        cut_example = {"history": qa_str}
        instruction_dic = {"instruction": background_prompt_dic['history_instruction'].format_map(cut_example),
                           "question": example['qas'][history_len]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][history_len]['answer']
    else:
        # 没有选择history
        instruction_dic = {"instruction": background_prompt_dic['no_history_instruction'],
                           "question": example['qas'][0]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][0]['answer']

    return prompt_input, target_answer


if __name__ == '__main__':
    example_str = """{"context": "sentimental", "prompt": "I remember going to the fireworks with my best friend. There was a lot of people_comma_ but it only felt like us in the world.", "conv_id": "hit:0_conv:1", "qas": [{"question": "I remember going to see the fireworks with my best friend. It was the first time we ever spent time alone together. Although there was a lot of people_comma_ we felt like the only people in the world.", "turn_id": 0, "answer": "Was this a friend you were in love with_comma_ or just a best friend?"}, {"question": "This was a best friend. I miss her.", "turn_id": 1, "answer": "Where has she gone?"}, {"question": "We no longer talk.", "turn_id": 2, "answer": "Oh was this something that happened because of an argument?"}]}"""
    example = json.loads(example_str)
    prompt_input, target_answer = get_prompt_input(example)
    print(f"prompt_input:\n{prompt_input}")
    print(f"target_answer:\n{target_answer}")
