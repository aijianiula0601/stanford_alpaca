import sys

pdj = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/eval/transformers_jh/src"
sys.path.append(pdj)
import transformers

model_dir = '/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun_conversation/ft_outs/checkpoint-2300'

tokenizer = transformers.AutoTokenizer.from_pretrained(model_dir, use_fast=False)
print("load model done!")

# prompt = "hello, how do you do?"
# input_ids = tokenizer(prompt).input_ids
# print("---input_ids:", input_ids)

output_ids = [2277, 29937]
output = tokenizer.decode(output_ids, skip_special_tokens=False)

print(f"----aa{output}bb!")
