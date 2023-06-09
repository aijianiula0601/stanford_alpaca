import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch

os.environ["CUDA_VISIBLE_DEVICES"] = "3"

# 模型下载：git clone https://huggingface.co/tiiuae/falcon-7b
model = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/falcon-7b"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
)
print("----load model done!----")

sequences = pipeline(
    "Girafatron is obsessed with giraffes, the most glorious animal on the face of this Earth. Giraftron believes all other animals are irrelevant when compared to the glorious majesty of the giraffe.\nDaniel: Hello, Girafatron!\nGirafatron:",
    max_length=200,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
)

print("-" * 50 + "output:" + "-" * 50)
for seq in sequences:
    print(f"Result: {seq['generated_text']}")
print("-" * 50 + "output:" + "-" * 50)
