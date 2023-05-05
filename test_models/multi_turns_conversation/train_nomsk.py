#    Copyright 2023 Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import os
import sys
import copy
import logging
from tqdm import tqdm
import json
import setproctitle
from dataclasses import dataclass, field
from typing import Optional, Dict, Sequence

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

import torch
import transformers
from torch.utils.data import Dataset
from transformers import Trainer
from test_models.multi_turns_conversation.data_utils import get_dataset_prompt

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"
DEFAULT_SEGMENT_TOKEN = "\n###"


@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="facebook/opt-125m")


@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the training data."})


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."},
    )


def safe_save_model_for_hf_trainer(trainer: transformers.Trainer, output_dir: str):
    """Collects the state dict and dump to disk."""
    state_dict = trainer.model.state_dict()
    if trainer.args.should_save:
        cpu_state_dict = {key: value.cpu() for key, value in state_dict.items()}
        del state_dict
        trainer._save(output_dir, state_dict=cpu_state_dict)  # noqa


def smart_tokenizer_and_embedding_resize(
        special_tokens_dict: Dict,
        tokenizer: transformers.PreTrainedTokenizer,
        model: transformers.PreTrainedModel,
):
    """Resize tokenizer and embedding.

    Note: This is the unoptimized version that may make your embedding size not be divisible by 64.
    """
    num_new_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    if num_new_tokens > 0:
        input_embeddings = model.get_input_embeddings().weight.data
        output_embeddings = model.get_output_embeddings().weight.data

        input_embeddings_avg = input_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)
        output_embeddings_avg = output_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)

        input_embeddings[-num_new_tokens:] = input_embeddings_avg
        output_embeddings[-num_new_tokens:] = output_embeddings_avg


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


def _tokenize_string(text, tokenizer: transformers.PreTrainedTokenizer):
    tokenized = tokenizer(
        text,
        return_tensors="pt",
        padding="longest",
        max_length=tokenizer.model_max_length,
        truncation=True,
    )
    tokenized_ids = tokenized.input_ids[0]
    tokenized_ids_len = tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item()
    return tokenized_ids, tokenized_ids_len


def _prompt_input(background):
    return background


def _preprocess_example(conversation_dic: Dict, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int):
    """
    :param token_max_len: limit number of token ids
    :param conversation_dic: example:{
        "background":"---",
        "human_name":"a",
        "bot_name":"b",
        "qas":{
            "turn_0":{"question":"---","answer":"---"},
            ...
            "turn_n":{"question":"---","answer":"---"}
        }
    }
    :param tokenizer: tokenizer model
    :return: dic
    """
    dataset_name = conversation_dic['dataset_name']
    default_segment_token_ids, default_segment_token_ids_len = _tokenize_string(DEFAULT_SEGMENT_TOKEN, tokenizer)

    turn_n = len(conversation_dic["qas"])
    human_name = conversation_dic['human_name']
    bot_name = conversation_dic['bot_name']
    header = get_dataset_prompt(dataset_name, human_name, bot_name, background=conversation_dic['background'])
    head_ids, header_ids_len = _tokenize_string(header, tokenizer)

    input_ids_tensor_list = [head_ids]

    for i in range(turn_n):
        cur_turn_qa = conversation_dic['qas'][f'turn_{i}']
        cur_question_string = human_name + ": " + cur_turn_qa["question"]
        cur_question_string_token_ids, cur_question_string_token_ids_len = _tokenize_string(cur_question_string,
                                                                                            tokenizer)
        cur_answer_string = bot_name + ": " + cur_turn_qa["answer"]
        cur_answer_string_token_ids, cur_answer_string_token_ids_len = _tokenize_string(cur_answer_string, tokenizer)

        if header_ids_len + default_segment_token_ids_len + cur_question_string_token_ids_len + default_segment_token_ids_len + cur_answer_string_token_ids_len > token_max_len:
            break

        # question
        input_ids_tensor_list.append(default_segment_token_ids)
        input_ids_tensor_list.append(cur_question_string_token_ids)
        header_ids_len += default_segment_token_ids_len + cur_question_string_token_ids_len

        # answer
        input_ids_tensor_list.append(default_segment_token_ids)
        input_ids_tensor_list.append(cur_answer_string_token_ids)
        header_ids_len += default_segment_token_ids_len + cur_answer_string_token_ids_len

    input_ids = torch.cat(input_ids_tensor_list, dim=0)
    label_ids = copy.deepcopy(input_ids)

    return input_ids, label_ids


def preprocess(
        examples: Sequence[Dict],
        tokenizer: transformers.PreTrainedTokenizer,
        token_max_len: int
) -> Dict:
    """Preprocess the data by tokenizing."""
    input_ids_list = []
    labels_list = []

    for example in tqdm(examples):
        input_ids, labels = _preprocess_example(example, tokenizer, token_max_len)
        input_ids_list.append(input_ids)
        labels_list.append(labels)

    return dict(input_ids=input_ids_list, labels=labels_list)


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int):
        super(SupervisedDataset, self).__init__()
        logging.warning("Loading data...")
        list_data_dict = json.load(open(data_path))

        data_dict = preprocess(list_data_dict, tokenizer, token_max_len)

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])


@dataclass
class DataCollatorForSupervisedDataset(object):
    """Collate examples for supervised fine-tuning."""

    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances: Sequence[Dict]) -> Dict[str, torch.Tensor]:
        input_ids, labels = tuple([instance[key] for instance in instances] for key in ("input_ids", "labels"))
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        labels = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=IGNORE_INDEX)
        return dict(
            input_ids=input_ids,
            labels=labels,
            attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
        )


def make_supervised_data_module(tokenizer: transformers.PreTrainedTokenizer, data_args, token_max_len) -> Dict:
    """Make dataset and collator for supervised fine-tuning."""
    train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path=data_args.data_path, token_max_len=token_max_len)
    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)
    return dict(train_dataset=train_dataset, eval_dataset=None, data_collator=data_collator)


def train():
    setproctitle.setproctitle("stanford_alpaca_nomask")
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
    )

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
        padding_side="right",
        use_fast=False,
    )
    if tokenizer.pad_token is None:
        smart_tokenizer_and_embedding_resize(
            special_tokens_dict=dict(pad_token=DEFAULT_PAD_TOKEN),
            tokenizer=tokenizer,
            model=model,
        )
    if "llama" in model_args.model_name_or_path:
        tokenizer.add_special_tokens(
            {
                "eos_token": DEFAULT_EOS_TOKEN,
                "bos_token": DEFAULT_BOS_TOKEN,
                "unk_token": DEFAULT_UNK_TOKEN,
            }
        )

    data_module = make_supervised_data_module(tokenizer=tokenizer, data_args=data_args,
                                              token_max_len=training_args.model_max_length)
    trainer = Trainer(model=model, tokenizer=tokenizer, args=training_args, **data_module)
    trainer.train()
    trainer.save_state()
    safe_save_model_for_hf_trainer(trainer=trainer, output_dir=training_args.output_dir)


if __name__ == "__main__":
    train()
