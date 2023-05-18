import argparse
# import torch
import os
import json
from tqdm import tqdm
import shortuuid
import ray
import sys
import llama_api

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role-file", type=str, required=True)
    parser.add_argument("--chat-log", type=str, default="answer.jsonl")
    args = parser.parse_args()
    run_eval(args.model_id, args.role_file, args.question_file, args.answer_file, args.num_gpus)