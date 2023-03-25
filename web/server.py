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


model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/llama/new_llama_7b"
load_model(model_dir)

# temp_list = (list(range(10) + 1) * 0.1
temp_list = [round(0.1 * char, 2) for char in list(range(1, 11))]


def user(user_message, history):
    return "", history + [["Human: " + user_message, None]]


def bot(history, temperature=0.5, background=""):
    invitation = "Assistant: "
    human_invitation = "Human: "
    if history[-1][0] != "":

        fulltext = background + "\n" + "\n".join([i for item in history for i in item][:-1]) + "\n" + invitation
        # print(fulltext)

        generated_text = ""
        gen_in = tokenizer(fulltext, return_tensors="pt").input_ids.cuda()
        with torch.no_grad():
            generated_ids = generator(
                gen_in,
                max_new_tokens=200,
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

            text_without_prompt = generated_text[len(fulltext):]

        # text_without_prompt = "Yes"
        response = text_without_prompt

        response = response.split(human_invitation)[0].strip()
        history[-1][-1] = (invitation + response)

        print("\n".join([i for item in history for i in item]))
        return history, temperature, background
    else:
        print("\n".join([i for item in history for i in item]))
        # history_show_list = [char.strip() for char in history]
        # history_show = "\n".join(history)

        return history, temperature, background


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
            background = gr.Textbox(lines=5, placeholder="设置聊天背景 ...只能用英文", label="背景")
            msg = gr.Textbox(placeholder="输入内容(Enter确定)", label="输入")

        with gr.Column():
            clear = gr.Button("清空聊天记录")
            chatbot = gr.Chatbot(label="聊天记录")

    msg.submit(user, [msg, chatbot],
               [msg, chatbot], queue=False).then(
        bot, [chatbot, selected_temp, background],
        [chatbot, selected_temp, background]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

# To create a public link, set `share=True` in `launch()`.
demo.launch(server_name="202.168.100.178", server_port=8099)
