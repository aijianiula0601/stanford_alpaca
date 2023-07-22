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
import json
import pickle
import setproctitle
from dataclasses import dataclass, field
from typing import Optional, Dict, Sequence
from joblib import Parallel, delayed
import random

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

import torch
import transformers
from torch.utils.data import Dataset
from transformers import Trainer

from dataset.data_utils import *

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"  # 修改为跟vicuna-7b的一样
DEFAULT_BOS_TOKEN = "<s>"  # 修改为跟vicuna-7b的一样
DEFAULT_UNK_TOKEN = "<unk>"  # 修改为跟vicuna-7b的一样
DEFAULT_SEGMENT_TOKEN = "### "


@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="facebook/opt-125m")


@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the training data."})
    lazy_load: bool = field(default=True)
    mask_head: bool = field(default=False)
    mask_question: bool = field(default=False)
    mask_except_last_answer: bool = field(default=False)
    data_len: int = field(default=-1)
    preload_n: int = field(default=5000)


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."},
    )
    process_name: str = field(default="train_multitype_data")


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


def _preprocess_example(conversation_dic: Dict, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int,
                        mask_head: bool, mask_question: bool, mask_except_last_answer: bool):
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
    dataset_name = conversation_dic[DATASET_KEY]

    ignore_token_index_list = []
    turn_n = len(conversation_dic[QAS_KEY])
    human_name = conversation_dic[HUMAN_NAME_KEY]
    bot_name = conversation_dic[BOT_NAME_KEY]
    header = get_dataset_prompt(dataset_name, human_name, bot_name, background=conversation_dic[BACKGROUND_KEY])
    head_ids, header_ids_len = _tokenize_string(header, tokenizer)

    if header_ids_len >= token_max_len:
        return None, None

    # mask head
    if mask_head:
        ignore_token_index_list.append((0, header_ids_len))  # mask index
    input_ids_tensor_list = [head_ids]

    for i in range(turn_n):
        cur_turn_qa = conversation_dic[QAS_KEY][f'{TURN_KEY}_{i}']

        if cur_turn_qa[QUESTION_KEY].strip() == "" or cur_turn_qa[ANSWER_KEY].strip() == "":
            break
        # mask question start index
        ignore_start_index = header_ids_len - 1
        # ------------
        # question
        # ------------
        cur_question_string = DEFAULT_SEGMENT_TOKEN + human_name + ": " + cur_turn_qa[
            QUESTION_KEY] + DEFAULT_SEGMENT_TOKEN + bot_name + ": "
        cur_question_string_token_ids, cur_question_string_token_ids_len = _tokenize_string(cur_question_string,
                                                                                            tokenizer)

        # 去掉开头为1的id
        assert cur_question_string_token_ids[0] == 1
        cur_question_string_token_ids = cur_question_string_token_ids[1:]
        cur_question_string_token_ids_len -= 1

        header_ids_len += cur_question_string_token_ids_len
        ignore_end_index = header_ids_len
        if header_ids_len > token_max_len:
            break

        # ------------
        # answer
        # ------------
        cur_answer_string = cur_turn_qa[ANSWER_KEY] + DEFAULT_EOS_TOKEN
        cur_answer_string_token_ids, cur_answer_string_token_ids_len = _tokenize_string(cur_answer_string, tokenizer)

        # 去掉开头为1的id
        assert cur_answer_string_token_ids[0] == 1
        cur_answer_string_token_ids = cur_answer_string_token_ids[1:]
        cur_answer_string_token_ids_len -= 1

        header_ids_len += cur_answer_string_token_ids_len
        if header_ids_len > token_max_len:
            break

        # 问题和答案都不超过长度才加入
        input_ids_tensor_list.append(cur_question_string_token_ids)
        input_ids_tensor_list.append(cur_answer_string_token_ids)
        if mask_question:
            ignore_token_index_list.append((ignore_start_index, ignore_end_index))  # mask index

    if len(input_ids_tensor_list) <= 1:
        # 只有head,没有qa的情况情况下，直接过滤。
        return None, None

    input_ids = torch.cat(input_ids_tensor_list, dim=0)
    label_ids = copy.deepcopy(input_ids)
    for ignore_start_i, ignore_end_i in ignore_token_index_list:
        label_ids[ignore_start_i:ignore_end_i] = IGNORE_INDEX

    # 最后一个answer前面的所有都mask
    if mask_except_last_answer and len(ignore_token_index_list) > 0:
        _, ignore_end_i = ignore_token_index_list[-1]
        label_ids[:ignore_end_i] = IGNORE_INDEX

    return input_ids, label_ids


def preprocess(
        examples: Sequence[Dict],
        tokenizer: transformers.PreTrainedTokenizer,
        token_max_len: int,
        mask_head: bool, mask_question: bool, mask_except_last_answer: bool
) -> Dict:
    """Preprocess the data by tokenizing."""
    input_ids_list = []
    labels_list = []

    skip_head_too_long_n = 0
    error_n = 0
    all_n = 0
    for example in tqdm(examples):
        all_n += 1
        try:
            input_ids, labels = _preprocess_example(example, tokenizer, token_max_len, mask_head, mask_question,
                                                    mask_except_last_answer)
            if input_ids is not None and labels is not None:
                input_ids_list.append(input_ids)
                labels_list.append(labels)
            else:
                skip_head_too_long_n += 1
        except Exception as e:
            logging.error(f"---------error:{e},example:\n{json.dumps(example)}")
            error_n += 1
            pass

    logging.info(f"---------all_n:{all_n},skip_head_too_long:{skip_head_too_long_n},error_n:{error_n}")

    return dict(input_ids=input_ids_list, labels=labels_list)


class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int, mask_head: bool,
                 mask_question: bool, mask_except_last_answer: bool, data_len: int, preload_n: 5000):
        super(LazySupervisedDataset, self).__init__()
        self.tokenizer = tokenizer
        self.f = data_path
        self.token_max_len = token_max_len
        self.mask_head = mask_head
        self.mask_except_last_answer = mask_except_last_answer
        self.mask_question = mask_question
        assert data_len > preload_n
        self.preload_n = preload_n
        self.data_len = data_len
        self.opened_file = open(data_path)
        self.preload_data_list = []
        self.preload_data()

    def preload_data(self):
        if len(self.preload_data_list) < self.preload_n:
            for example in self.opened_file:
                self.preload_data_list.append(example)
                if len(self.preload_data_list) >= self.preload_n:
                    break

        # 发现读取到文件尾部了，重新打开文件
        if len(self.preload_data_list) < self.preload_n:
            self.opened_file = open(self.f)
            for example in self.opened_file:
                self.preload_data_list.append(example)
                if len(self.preload_data_list) >= self.preload_n:
                    break

    def get_one_line(self):
        random_i = random.randint(0, len(self.preload_data_list) - 1)
        example = self.preload_data_list[random_i]
        del self.preload_data_list[random_i]
        self.preload_data()
        return json.loads(example)

    def __len__(self):
        return self.data_len

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        example = self.get_one_line()
        input_ids, labels = _preprocess_example(example, self.tokenizer, self.token_max_len,
                                                self.mask_head, self.mask_question, self.mask_except_last_answer)
        while input_ids is None or labels is None:
            example = self.get_one_line()
            input_ids, labels = _preprocess_example(example, self.tokenizer, self.token_max_len,
                                                    self.mask_head, self.mask_question, self.mask_except_last_answer)
            if input_ids is None or labels is None:
                logging.warning(f"----input_ids or labels is None,resample!")

        return dict(input_ids=input_ids, labels=labels)


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
    logging.warning(f"-----lazy_load:{data_args.lazy_load}")
    logging.warning(f"-----mask_head:{data_args.mask_head}, mask_question:{data_args.mask_question}")
    logging.warning("----loading data with lazy!")
    train_dataset = LazySupervisedDataset(tokenizer=tokenizer, data_path=data_args.data_path,
                                          token_max_len=token_max_len, mask_head=data_args.mask_head,
                                          mask_question=data_args.mask_question,
                                          mask_except_last_answer=data_args.mask_except_last_answer,
                                          data_len=data_args.data_len, preload_n=data_args.preload_n)

    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)
    return dict(train_dataset=train_dataset, eval_dataset=None, data_collator=data_collator)


def train():
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    setproctitle.setproctitle(training_args.process_name)

    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=True,
        cache_dir=training_args.cache_dir,
    )

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
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
