import json
import random
import copy
import logging
import json
from typing import Optional, Dict, Sequence

import torch
import transformers
from torch.utils.data import Dataset

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"
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
save_f = f"{base_dir}/prepared_personality.json"


def qas_to_history_str(qas_list):
    qas_str = []
    for qa in qas_list:
        question = qa['question']
        answer = qa['answer']

        qas_str.append(f"Question: {question}\nAnswer: {answer}")

    return "\n".join(qas_str)


def get_prompt_input(example):
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


def _tokenize_fn(strings: Sequence[str], tokenizer: transformers.PreTrainedTokenizer) -> Dict:
    """Tokenize a list of strings."""
    tokenized_list = [
        tokenizer(
            text,
            return_tensors="pt",
            padding="longest",
            max_length=tokenizer.model_max_length,
            truncation=True,
        )
        for text in strings
    ]
    input_ids = labels = [tokenized.input_ids[0] for tokenized in tokenized_list]
    input_ids_lens = labels_lens = [
        tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item() for tokenized in tokenized_list
    ]
    return dict(
        input_ids=input_ids,
        labels=labels,
        input_ids_lens=input_ids_lens,
        labels_lens=labels_lens,
    )


def preprocess(
        sources: Sequence[str],
        targets: Sequence[str],
        tokenizer: transformers.PreTrainedTokenizer,
) -> Dict:
    """Preprocess the data by tokenizing."""
    examples = [s + t for s, t in zip(sources, targets)]
    examples_tokenized, sources_tokenized = [_tokenize_fn(strings, tokenizer) for strings in (examples, sources)]
    input_ids = examples_tokenized["input_ids"]
    labels = copy.deepcopy(input_ids)
    for label, source_len in zip(labels, sources_tokenized["input_ids_lens"]):
        label[:source_len] = IGNORE_INDEX
    return dict(input_ids=input_ids, labels=labels)


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer):
        super(SupervisedDataset, self).__init__()
        logging.warning("Loading data...")
        list_data_dict = json.load(open(data_path))

        logging.warning("Formatting inputs...")
        prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
        sources = [
            prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)
            for example in list_data_dict
        ]
        targets = [f"{example['output']}{tokenizer.eos_token}" for example in list_data_dict]

        logging.warning("Tokenizing inputs... This may take some time...")
        data_dict = preprocess(sources, targets, tokenizer)

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])


if __name__ == '__main__':
    # example_str = """{"profile_information": "i love to bake cakes. i have a twin brother. my favorite book is david copperfield. i m really short.", "qas": [{"question": "hello how are you tonight", "answer": "i am okay . i wish i was more tired though . you ?", "turn_i": 0}, {"question": "my children let me down so i have been better", "answer": "what did they do that disappointed you ?", "turn_i": 1}, {"question": "married ugly people i am with miss usa", "answer": "wow . that is too bad . i do not have kids . i have brothers , twins .", "turn_i": 2}, {"question": "wow that is cool are ou a twin too or just them", "answer": "no , just them . it was lonely growing up . do you have siblings ?", "turn_i": 3}, {"question": "no i do not have any it was boring growing up", "answer": "yeah . i always bake cookies when i am bored . do you have a hobby ?", "turn_i": 4}, {"question": "i have maids so i do not have to bake", "answer": "i love baking . maids huh ? fancy . are you rich ?", "turn_i": 5}, {"question": "i am a little rich i suppose", "answer": "i wish i was . what do you do for a living ?", "turn_i": 6}]}"""
    # example = json.loads(example_str)
    # prompt_input, target_answer = get_prompt_input(example)
    # print(f"prompt_input:\n{prompt_input}")
    # print(f"target_answer:\n{target_answer}")

    base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/personaChat"
    data_path = f"{base_dir}/prepared_personality.json"
    model_name_or_path = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name_or_path,
        padding_side="right",
        use_fast=False,
    )

    print("load tokenizer done!")
    spd = SupervisedDataset(data_path=data_path, tokenizer=tokenizer)
    print(spd.__getitem__(0))
