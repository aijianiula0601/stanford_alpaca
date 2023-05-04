import os
import sys

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"--pdj:{pdj}")
sys.path.append(pdj)
import transformers
from test_models.multi_turns_conversation.train import smart_tokenizer_and_embedding_resize, DEFAULT_PAD_TOKEN, \
    DEFAULT_BOS_TOKEN, DEFAULT_EOS_TOKEN, DEFAULT_UNK_TOKEN, _tokenize_string

if __name__ == '__main__':
    model_name_or_path = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
    model_max_length = 512
    cache_dir = '/mnt/cephfs/hjh/tmp'

    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        cache_dir=cache_dir,
    )

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name_or_path,
        cache_dir=cache_dir,
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

    print("load model done!")

    text = "hello, how do you do?"

    text_ids, text_ids_len = _tokenize_string(text, tokenizer)
    print("-----text_ids:", text_ids)
    print("-----text_ids_len:", text_ids_len)
