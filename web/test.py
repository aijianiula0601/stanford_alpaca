PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
}

prompt_input = PROMPT_DICT['prompt_input']

example = {
    "instruction": (
        "The following is a friendly chat message between human and ai. Ai plays the role of a little girl named Alice. Alice is a rich girl who studies in junior high school. The human is a very friendly excellent student, both of them like to go to the library.\n"
        "Current conversation:"
        ),
    "input": (
        "human: not much, just wondering if you want to come to the library with me?\n"
        "Alice: sure, why not? let’s go!\n"
        "human: great! see you there!\n"
        "Alice: bye!\n"
        "human: I've arrived at the library. Where are you?\n"
        "Alice: 5 minutes!\n"
        "human: I have finished my study. I am so tired. Would you like to have dinner together?\n"
        "Alice: sure, that sounds fun! Let’s go!\n"
        "human: What do you like to eat?\n"
    ),
}
prompt_input = prompt_input.format_map(example)

print(prompt_input)
