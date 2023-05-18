import argparse
# import torch
import os
import json
from tqdm import tqdm
import shortuuid
import ray
import sys
import llama_api
from prompt import Conversation
from utils import disable_torch_init

def run_eval(model_id, role_file, question_file, answer_file, num_gpus):
    # split question file into num_gpus files
    ques_jsons = []
    with open(os.path.expanduser(question_file), "r") as ques_file:
        for line in ques_file:
            ques_jsons.append(line)
    new_ans_jsons = get_model_answers_api(model_id, role_file, ques_jsons)
    with open(os.path.expanduser(answer_file), "w") as ans_file:
        # for line in ans_jsons:
        #     ans_file.write(json.dumps(line) + "\n")
        json.dump(new_ans_jsons, ans_file)


def get_model_answers_api(model_id, role_file, question_jsons):

    roles_desc = []
    roles_json = json.load(open(role_file))
    for key, value in roles_json.items():
        roles_desc.append([key, value])
    result = {}
    for key, role_desc in roles_desc:
        role_human = role_desc['role_human']
        role_ai = role_desc['role_ai']
        role_back = role_desc['background']
        role_dict = {'user': role_human, 'assistant': role_ai}
        ans_jsons = []
        for i, line in enumerate(tqdm(question_jsons)):
            ques_json = json.loads(line)
            idx = ques_json["question_id"]
            qs = ques_json["text"]
            message_list_org = [
            {'role': 'system',
             'content': role_back},
            ]
            message_list_org.append({
                'role' : 'user',
                'content' : qs
            })
            if model_id == 'llama_respond_context':
                outputs = llama_api.llama_respond_context(message_list_org, role_dict)
            elif model_id == 'llama_respond':
                outputs = llama_api.llama_respond(message_list_org, role_dict)
            ans_id = shortuuid.uuid()
            ans_jsons.append({"question_id": idx,
                            "text": outputs,
                            "answer_id": ans_id,
                            "model_id": model_id,
                            "role_human": role_human,
                            "role_ai" : role_ai,
                            "metadata": {}})
        result[key] = ans_jsons
    return result

# @torch.inference_mode()
# def get_model_answers(model_path, model_id, role_file, question_jsons):
#     disable_torch_init()
#     if 'old' in model_id:
#         sys.path.append('/mnt/cephfs/liujunshi_data/Projects/bigo_stanford_alpaca/lib/transformers_jh/src')
#     else:
#         sys.path.append('/mnt/cephfs/liujunshi_data/Projects/bigo_stanford_alpaca/lib/transformers/src')
#     from transformers import AutoTokenizer, AutoModelForCausalLM
#     model_path = os.path.expanduser(model_path)
#     tokenizer = AutoTokenizer.from_pretrained(model_path)
#     model = AutoModelForCausalLM.from_pretrained(model_path,
#         torch_dtype=torch.float16).cuda()
    
#     # load roles
#     roles_desc = []
#     roles_json = json.load(open(role_file))
#     for key, value in roles_json.items():
#         roles_desc.append([key, value])

#     result = {}

#     for key, role_desc in roles_desc:
#         role_human = role_desc['role_human']
#         role_ai = role_desc['role_ai']
#         role_back = role_desc['background']
#         conv_roles = Conversation(
#             system = "{background}The following is a chat message between {role_a} and {role_b} using English Language. Question and answer,  forbid the output of multiple rounds.\n\nCurrent conversation:\n\n###{history}",
#             roles = [role_human, role_ai],
#             background = role_back,
#             messages = (),
#             offset = 2,
#         )
#         ans_jsons = []
#         for i, line in enumerate(tqdm(question_jsons)):
#             ques_json = json.loads(line)
#             idx = ques_json["question_id"]
#             qs = ques_json["text"]
#             conv = conv_roles.copy()
#             conv.append_message(conv.roles[0], qs)
#             prompt = conv.get_chat_prompt()
#             if conv.messages[-1][0] == conv.roles[0]:
#                 prompt += conv.roles[1]+': '
#             elif conv.messages[-1][0] == conv.roles[1]:
#                 prompt += conv.roles[1]+': '
#             else:
#                 raise ValueError(f"Invalid roles: {conv.messages[-1][0]}")
#             inputs = tokenizer([prompt])
#             output_ids = model.generate(
#                 torch.as_tensor(inputs.input_ids).cuda(),
#                 do_sample=True,
#                 temperature=0.7,
#                 max_new_tokens=1024)
#             outputs = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
#             try:
#                 index = outputs.index(conv.sep, len(prompt))
#             except ValueError:
#                 outputs += conv.sep
#                 index = outputs.index(conv.sep, len(prompt))

#             outputs = outputs[len(prompt) + 2:index].strip()
#             ans_id = shortuuid.uuid()
#             ans_jsons.append({"question_id": idx,
#                             "text": outputs,
#                             "answer_id": ans_id,
#                             "model_id": model_id,
#                             "role_human": role_human,
#                             "role_ai" : role_ai,
#                             "metadata": {}})
#         result[key] = ans_jsons
#     return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--role-file", type=str, required=True)
    parser.add_argument("--question-file", type=str, required=True)
    parser.add_argument("--answer-file", type=str, default="answer.jsonl")
    parser.add_argument("--num-gpus", type=int, default=1)
    args = parser.parse_args()
    run_eval(args.model_id, args.role_file, args.question_file, args.answer_file, args.num_gpus)
