import os
import sys
import torch
import gradio as gr

pdj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pdj)
import transformers

model = None
tokenizer = None
generator = None

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
}


def load_model(model_name, eight_bit=0, device_map="auto"):
    global model, tokenizer, generator

    print("Loading " + model_name + "...")

    if device_map == "zero":
        device_map = "balanced_low_0"

    # config
    gpu_count = torch.cuda.device_count()
    print('gpu_count', gpu_count)

    tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_name,
        # device_map=device_map,
        # device_map="auto",
        torch_dtype=torch.float16,
        # max_memory = {0: "14GB", 1: "14GB", 2: "14GB", 3: "14GB",4: "14GB",5: "14GB",6: "14GB",7: "14GB"},
        # load_in_8bit=eight_bit,
        low_cpu_mem_usage=True,
        load_in_8bit=False,
        cache_dir="cache"
    ).cuda()

    generator = model.generate


# model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/ft_52k/llama-7b-hf_train_out/checkpoint-250"
load_model(model_dir)

# temp_list = (list(range(10) + 1) * 0.1
temp_list = [round(0.1 * char, 2) for char in list(range(1, 11))]


def user(user_message, history):
    return "", history + [[user_message, None]]


def bot(history, temperature=0.5, max_gen_len=256):
    user_message = history[-1][0]
    gen_in = tokenizer(user_message, return_tensors="pt").input_ids.cuda()

    with torch.no_grad():
        generated_ids = generator(
            gen_in,
            max_new_tokens=max_gen_len,
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
        generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0]  # for some reason, batch_decode returns an array of one element?

    print('-' * 20 + "response" + "-" * 20)
    print("-" * 50)

    history[-1][-1] = generated_text

    print("\n".join([i for item in history for i in item]))
    return history, temperature, max_gen_len


# --------------------------------------------------------
# 页面构建
# --------------------------------------------------------

with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# llama 7B Alpaca English")
    with gr.Row():
        with gr.Column():
            selected_temp = gr.Slider(0, 1, value=0.5, label="Temperature超参,调的越小越容易输出常见字",
                                      interactive=True)
            max_gen_len = gr.Slider(100, 1000, value=256, label="最大生成字符数", interactive=True)
            msg = gr.Textbox(placeholder="输入内容(Enter确定)", label="输入")

        with gr.Column():
            clear = gr.Button("清空聊天记录")
            chatbot = gr.Chatbot(label="聊天记录")

    msg.submit(user, [msg, chatbot],
               [msg, chatbot], queue=False).then(
        bot, [chatbot, selected_temp, max_gen_len],
        [chatbot, selected_temp, max_gen_len]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

import random

# To create a public link, set `share=True` in `launch()`.
# demo.launch(server_name="0.0.0.0", server_port=8094)
demo.launch(server_name="202.168.100.178", server_port=random.randint(8000, 9000))
