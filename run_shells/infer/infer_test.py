import sys
import os


pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pdj)

import transformers

# -----------------------
# test tokenizer
# -----------------------

model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
tokenizer = transformers.LLaMATokenizer.from_pretrained(model_dir)

# print("load model done!")

# text = "hello"
# gen_in = tokenizer(text, return_tensors="pt")
# print("output:", gen_in)


vocab = tokenizer.get_vocab()

print(vocab.keys())
# print(len(vocab.keys()))


