import os
import json
import sys
import setproctitle
import transformers
import pickle

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from test_models.mask_header_answer.train_multi_round_mask_answer_multitype_dataset import _preprocess_example
from test_models.mask_header_answer.train_multi_round_mask_answer_multitype_dataset import *


def my_preprocess(
        examples: Sequence[Dict],
        tokenizer: transformers.PreTrainedTokenizer,
        token_max_len: int
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
            input_ids, labels = _preprocess_example(example, tokenizer, token_max_len)
            if input_ids is not None and labels is not None:
                input_ids_list.append(list(input_ids.numpy()))
                labels_list.append(list(labels.numpy()))
            else:
                skip_head_too_long_n += 1
        except Exception as e:
            logging.error(f"---------error:{e}")
            error_n += 1
            pass

    logging.info(f"---------all_n:{all_n},skip_head_too_long:{skip_head_too_long_n},error_n:{error_n}")

    return dict(input_ids=input_ids_list, labels=labels_list)


def train():
    setproctitle.setproctitle("pre_token")
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

    list_data_dict = json.load(open(data_args.data_path))
    data_dict = preprocess(list_data_dict, tokenizer, training_args.model_max_length)

    save_f = data_args.data_path + "_tokenid.obj"

    pickle.dump(data_dict, open(save_f, 'wb'))
    print(f"save to:{save_f}")

    # loaded_data_dic = pickle.load(open(save_f, 'rb'))  # 反序列化
    # print(loaded_data_dic)


if __name__ == '__main__':
    train()
