import logging
import orjson
import os
from flask import Flask, request, Response
import setproctitle
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers

from logger import MyLogger

os.environ["CUDA_VISIBLE_DEVICES"] = "3"

logger = MyLogger.__call__().get_logger()

app = Flask(__name__)
app.logger.disabled = True
logging.getLogger("werkzeug").disabled = True
logging.getLogger().setLevel(logging.WARNING)

setproctitle.setproctitle("test_infer_model")


def load_model(model_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    pipeline = transformers.pipeline(
        "text-generation",
        model=model_dir,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
    )

    return pipeline, tokenizer


# 模型下载：git clone https://huggingface.co/tiiuae/falcon-7b
model_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_models/falcon-7b"
infer_model, tokenizer = load_model(model_dir)
print("---load model done!---")


def bot(prompt_input):
    sequences = infer_model(
        prompt_input,
        max_length=256,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )
    print("-" * 50 + "model response:" + "-" * 50)
    print(f"{sequences}")
    print("-" * 100)

    return sequences[0]['generated_text']


@app.route("/api", methods=["POST"])
def receive():
    try:
        params = orjson.loads(request.data)
    except orjson.JSONDecodeError:
        logger.error("Invalid json format in request data: [{}].".format(request.data))
        res = {"status": 400, "error_msg": "Invalid json format in request data.", "server_info": "", }
        return Response(orjson.dumps(res), mimetype="application/json;charset=UTF-8", status=200)

    if 'prompt_input' not in params:
        logger.error("Invalid json request.")
        res = {"status": 400, "error_msg": "Invalid json request.", "server_info": "", }
        return Response(orjson.dumps(res), mimetype="application/json;charset=UTF-8", status=200)

    prompt_input = params.get('prompt_input', "")
    print("-" * 50 + "prompt input:" + "-" * 50)
    print(prompt_input)
    print("-" * 100)

    result = bot(prompt_input)

    res = {"status": 200, "result": result, "error_msg": "", "server_info": ""}
    return Response(orjson.dumps(res), mimetype="application/json;charset=UTF-8", status=200)


if __name__ == '__main__':
    app.run(debug=False, host="202.168.114.102", port=6024)
