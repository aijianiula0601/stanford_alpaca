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
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"
DEFAULT_SEGMENT_TOKEN = "### "
DEFAULT_END_TOKEN = "\n"


@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="facebook/opt-125m")


@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the training data."})
    lazy_load: bool = field(default=True)
    mask_head: bool = field(default=False)
    mask_question: bool = field(default=False)


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
                        mask_head: bool, mask_question: bool):
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
            return None, None

        # mask question start index
        ignore_start_index = header_ids_len - 1
        # ------------
        # question
        # ------------
        cur_question_string = DEFAULT_SEGMENT_TOKEN + human_name + ": " + cur_turn_qa[
            QUESTION_KEY] + DEFAULT_SEGMENT_TOKEN
        cur_question_string_token_ids, cur_question_string_token_ids_len = _tokenize_string(cur_question_string,
                                                                                            tokenizer)

        header_ids_len += cur_question_string_token_ids_len
        ignore_end_index = header_ids_len
        if header_ids_len > token_max_len:
            break

        # ------------
        # answer
        # ------------
        cur_answer_string = DEFAULT_END_TOKEN + bot_name + ": " + cur_turn_qa[ANSWER_KEY] + DEFAULT_END_TOKEN
        cur_answer_string_token_ids, cur_answer_string_token_ids_len = _tokenize_string(cur_answer_string, tokenizer)
        header_ids_len += cur_answer_string_token_ids_len
        if header_ids_len > token_max_len:
            break

        # 问题和答案都不超过长度才加入
        input_ids_tensor_list.append(cur_question_string_token_ids)
        input_ids_tensor_list.append(cur_answer_string_token_ids)
        # -----sharegpt数据必须做mask
        if mask_question or dataset_name == SHAREGPT_DATASET_NAME:
            ignore_token_index_list.append((ignore_start_index, ignore_end_index))  # mask index

    if len(input_ids_tensor_list) <= 1:
        # 只有head,没有qa的情况情况下，直接过滤。
        return None, None

    input_ids = torch.cat(input_ids_tensor_list, dim=0)
    label_ids = copy.deepcopy(input_ids)
    for ignore_start_i, ignore_end_i in ignore_token_index_list:
        label_ids[ignore_start_i:ignore_end_i] = IGNORE_INDEX

    return input_ids, label_ids


def preprocess(
        examples: Sequence[Dict],
        tokenizer: transformers.PreTrainedTokenizer,
        token_max_len: int,
        mask_head: bool, mask_question: bool
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
            input_ids, labels = _preprocess_example(example, tokenizer, token_max_len, mask_head, mask_question)
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


def parallel_preprocess(examples: Sequence[Dict],
                        tokenizer: transformers.PreTrainedTokenizer,
                        token_max_len: int, mask_head: bool, mask_question: bool) -> Dict:
    logging.warning("--------parallel_preprocess... ---------")
    results = Parallel(n_jobs=40, backend="multiprocessing")(
        delayed(_preprocess_example)(example, tokenizer, token_max_len, mask_head, mask_question) for example in
        tqdm(examples))

    input_ids_list = []
    labels_list = []

    skip_head_too_long_n = 0
    error_n = 0
    all_n = 0
    for input_ids, labels in tqdm(results):
        all_n += 1
        try:
            if input_ids is not None and labels is not None:
                input_ids_list.append(input_ids)
                labels_list.append(labels)
            else:
                skip_head_too_long_n += 1
        except Exception as e:
            logging.error(f"---------error:{e}")
            error_n += 1
            pass

    logging.warning(
        f"[parallel_preprocess]---------all_n:{all_n},skip_head_too_long:{skip_head_too_long_n},error_n:{error_n}")

    return dict(input_ids=input_ids_list, labels=labels_list)


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int, mask_head: bool,
                 mask_question: bool):
        super(SupervisedDataset, self).__init__()
        logging.warning("Loading data...")

        tokenizer_file = f"{data_path}_tokenizer.obj"
        assert "checked" in data_path, f"--------必须保证加载的文件是经过检测的，执行multitype_dataset_pre_token.py后的文件，目前加载的文件为:{data_path}"

        if os.path.exists(tokenizer_file):
            data_dict = pickle.load(open(tokenizer_file, 'rb'))  # 反序列化
            logging.warning(f"loaded data from:{tokenizer_file}")
        else:
            list_data_dict = json.load(open(data_path))
            random.shuffle(list_data_dict)
            # data_dict = parallel_preprocess(list_data_dict, tokenizer, token_max_len)#测试了并不快
            data_dict = preprocess(list_data_dict, tokenizer, token_max_len, mask_head, mask_question)
            pickle.dump(data_dict, open(tokenizer_file, 'wb'))
            logging.warning(f"loaded data from:{data_path}")

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])


class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, token_max_len: int, mask_head: bool,
                 mask_question: bool):
        super(LazySupervisedDataset, self).__init__()
        self.tokenizer = tokenizer
        self.token_max_len = token_max_len
        self.mask_head = mask_head
        self.mask_question = mask_question
        self.list_data_dict = json.load(open(data_path))
        random.shuffle(self.list_data_dict)
        self.list_data_dict_len = len(self.list_data_dict)
        logging.warning(f"loaded org data list:{self.list_data_dict_len}!")

    def __len__(self):
        return self.list_data_dict_len

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        input_ids, labels = _preprocess_example(self.list_data_dict[i], self.tokenizer, self.token_max_len,
                                                self.mask_head, self.mask_question)
        while input_ids is None or labels is None:
            random_i = random.randint(0, self.list_data_dict_len - 1)
            input_ids, labels = _preprocess_example(self.list_data_dict[random_i], self.tokenizer, self.token_max_len,
                                                    self.mask_head, self.mask_question)
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
    if data_args.lazy_load:
        logging.warning("----loading data with lazy!")
        train_dataset = LazySupervisedDataset(tokenizer=tokenizer, data_path=data_args.data_path,
                                              token_max_len=token_max_len, mask_head=data_args.mask_head,
                                              mask_question=data_args.mask_question)
    else:
        train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path=data_args.data_path,
                                          token_max_len=token_max_len, mask_head=data_args.mask_head,
                                          mask_question=data_args.mask_question)
    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)
    return dict(train_dataset=train_dataset, eval_dataset=None, data_collator=data_collator)


def train():
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    setproctitle.setproctitle(training_args.process_name)

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
