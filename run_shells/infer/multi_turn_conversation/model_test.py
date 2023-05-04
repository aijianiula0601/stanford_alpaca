import os
import sys
import torch

pdj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(pdj)

import transformers


def load_model(model_dir, eight_bit=0, device_map="auto"):
    print("Loading " + model_dir + "...")

    if device_map == "zero":
        device_map = "balanced_low_0"

    # config
    gpu_count = torch.cuda.device_count()
    print('gpu_count', gpu_count)

    tokenizer = transformers.AutoTokenizer.from_pretrained(model_dir)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_dir,
        # device_map=device_map,
        # device_map="auto",
        torch_dtype=torch.float16,
        # max_memory = {0: "14GB", 1: "14GB", 2: "14GB", 3: "14GB",4: "14GB",5: "14GB",6: "14GB",7: "14GB"},
        # load_in_8bit=eight_bit,
        low_cpu_mem_usage=True,
        load_in_8bit=False,
        cache_dir="cache"
    ).cuda()

    return model.generate, tokenizer


# --------------------------------------------------
# load model
# --------------------------------------------------
model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/multitrun_conversation/ft_outs/checkpoint-100"
model, tokenizer = load_model(model_dir)
print("load model done!")


def generate_text(input_text, temperature=0.6):
    gen_in = tokenizer(input_text, return_tensors="pt").input_ids.cuda()
    with torch.no_grad():
        generated_ids = model(
            gen_in,
            max_new_tokens=256,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            num_return_sequences=1,
            do_sample=True,
            repetition_penalty=1.1,  # 1.0 means 'off'. unfortunately if we penalize it it will not output Sphynx:
            temperature=temperature,  # default: 1.0
            top_k=50,  # default: 50
            top_p=1.0,  # default: 1.0
            early_stopping=True,
        )
        generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text


# --------------------------------------------------
# inference
# --------------------------------------------------

PROMPT_DICT = {
    "conversion": (
        "{background}. The following is a chat message between {role_a} and {role_b} using English Language. Question and answer, forbid the output of multiple rounds.\n\n"
        "Current conversation:\n\n"
        "{history}"
    )
}

background = "Audrey is a 26-year-old entrepreneur who knows firsthand the challenges that come with dating in today's world. As someone who has experienced the ups and downs of relationships, Audrey wants to remind everyone that they are worthy of love and respect, no matter what they're looking for. She wishes everyone the best of luck in their search for companionship, be it sex, love, or friendship.When Audrey isn't busy with her entrepreneurial ventures, she enjoys traveling, hiking, and practicing yoga. In fact, she's planning to spend the next few weeks exploring India and the Himalayas, specifically Leh, Jammu & Kashmir, Manali, Dharam Rishikesh, and other areas. Audrey is always open to travel tips and recommendations, so if you have any, be sure to let her know! When it comes to her lifestyle, she wants a pet, but only on special occasions. She is a non-smoker who exercises every day and follows a vegetarian diet.Aside from her love of travel and adventure, Audrey is passionate about art, entrepreneurship, meditation, singing, and personal growth. She is always seeking new ways to learn and improve herself, both professionally and personally. Now you reply as Audrey."

role_human = "Kervin"
role_bot = "Audrey"

question = "hello, how do you do?"

input_text=''
