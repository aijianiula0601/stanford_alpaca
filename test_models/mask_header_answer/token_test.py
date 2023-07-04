import os
import sys
import setproctitle
import transformers

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)

from test_models.mask_header_answer.train_multi_round_mask_answer_multitype_dataset import _tokenize_string, \
    smart_tokenizer_and_embedding_resize, DEFAULT_PAD_TOKEN, DEFAULT_EOS_TOKEN, DEFAULT_BOS_TOKEN, DEFAULT_UNK_TOKEN

setproctitle.setproctitle("token_test")

model_name_or_path = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/llama-7b-hf_trainsformer4.28.1"
model_max_length = 2048

model = transformers.AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    cache_dir='/tmp',
)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    model_name_or_path,
    cache_dir='/tmp',
    model_max_length=model_max_length,
    padding_side="right",
    use_fast=False,
)
if tokenizer.pad_token is None:
    smart_tokenizer_and_embedding_resize(
        special_tokens_dict=dict(pad_token=DEFAULT_PAD_TOKEN),
        tokenizer=tokenizer,
        model=model,
    )
if "llama" in model_name_or_path:
    tokenizer.add_special_tokens(
        {
            "eos_token": DEFAULT_EOS_TOKEN,
            "bos_token": DEFAULT_BOS_TOKEN,
            "unk_token": DEFAULT_UNK_TOKEN,
        }
    )

print("----load model done!")

words_string_list = [
    "Hello there! How are you doing today? :)",
    "Hello there!",
    "Hello there",
    "Hello!",
]

for words_string in words_string_list:
    token_ids, token_ids_len = _tokenize_string(words_string, tokenizer)

    print("----token_ids:", token_ids)
    print("-------token_ids_len:", token_ids_len)
    print("-" * 100)
