import json
import random

background_prompt_dic = {
    "history_instruction": (
        "Let's play a role-playing dialogue. It will describe your profile information using the first person perspective:\n"
        "{profile_information}\n"
        "Your profile information has been described. Below is a history of the question and answer:\n"
        "{history}\n"
        "Please respond according to the question.\n"
    ),
    "no_history_instruction": (
        "Let's play a role-playing dialogue. It will describe your profile information using the first person perspective:\n"
        "{profile_information}\n"
        "Your profile information has been described. Please respond according to the question\n"
    )
}

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n Question: {question}\n Answer: "
    ),

}

base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/personaChat"
# save_f = f"{base_dir}/prepared_personality.json"
save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/personaChat/prepared_train_personality.json"

list_data_dict = json.load(open(save_f, "r"))
example = list_data_dict[random.randint(0, len(list_data_dict))]
print(json.dumps(example))


# example_str = """{"profile_information": "i love to bake cakes. i have a twin brother. my favorite book is david copperfield. i m really short.", "qas": [{"question": "hello how are you tonight", "answer": "i am okay . i wish i was more tired though . you ?", "turn_i": 0}, {"question": "my children let me down so i have been better", "answer": "what did they do that disappointed you ?", "turn_i": 1}, {"question": "married ugly people i am with miss usa", "answer": "wow . that is too bad . i do not have kids . i have brothers , twins .", "turn_i": 2}, {"question": "wow that is cool are ou a twin too or just them", "answer": "no , just them . it was lonely growing up . do you have siblings ?", "turn_i": 3}, {"question": "no i do not have any it was boring growing up", "answer": "yeah . i always bake cookies when i am bored . do you have a hobby ?", "turn_i": 4}, {"question": "i have maids so i do not have to bake", "answer": "i love baking . maids huh ? fancy . are you rich ?", "turn_i": 5}, {"question": "i am a little rich i suppose", "answer": "i wish i was . what do you do for a living ?", "turn_i": 6}]}"""
# example_str = """{"profile_information": "i love to bake cakes. i have a twin brother. my favorite book is david copperfield. i m really short.", "qas": [{"question": "hello how are you tonight", "answer": "i am okay . i wish i was more tired though . you ?", "turn_i": 0}]}"""
#
# # print(example_str)
# example = json.loads(example_str)


def qas_to_history_str(qas_list):
    qas_str = []
    for qa in qas_list:
        question = qa['question']
        answer = qa['answer']

        qas_str.append(f"Question: {question}\nAnswer: {answer}")

    return "\n".join(qas_str)


def get_prompt_input_random_qa(example):
    history_len = random.randint(0, len(example['qas']) - 1)
    if history_len > 0:
        cut_qas = example['qas'][:history_len]
        qa_str = qas_to_history_str(cut_qas)
        cut_example = {"profile_information": example['profile_information'], "history": qa_str}
        instruction_dic = {"instruction": background_prompt_dic['history_instruction'].format_map(cut_example),
                           "question": example['qas'][history_len]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][history_len]['answer']
    else:
        # 没有选择history
        cut_example = {"profile_information": example['profile_information']}
        instruction_dic = {"instruction": background_prompt_dic['no_history_instruction'].format_map(cut_example),
                           "question": example['qas'][0]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][0]['answer']

    return prompt_input, target_answer


def get_prompt_input(example):
    history_len = len(example['qas']) - 1
    if history_len > 0:
        cut_qas = example['qas'][:history_len]
        qa_str = qas_to_history_str(cut_qas)
        cut_example = {"profile_information": example['profile_information'], "history": qa_str}
        instruction_dic = {"instruction": background_prompt_dic['history_instruction'].format_map(cut_example),
                           "question": example['qas'][history_len]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][history_len]['answer']
    else:
        # 没有选择history
        cut_example = {"profile_information": example['profile_information']}
        instruction_dic = {"instruction": background_prompt_dic['no_history_instruction'].format_map(cut_example),
                           "question": example['qas'][0]['question']}

        prompt_input = PROMPT_DICT['prompt_input'].format_map(instruction_dic)
        target_answer = example['qas'][0]['answer']

    return prompt_input, target_answer
#
#
# prompt_input, target_answer = get_prompt_input(example)
# print(f"prompt_input:\n{prompt_input}")
# print(f"target_answer:\n{target_answer}")
#
