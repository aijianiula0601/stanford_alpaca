"""Generate answers with GPT-3.5"""
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import argparse
import json
import os
import time
import concurrent.futures

import openai
import tqdm
import shortuuid

MODEL = 'gpt-3.5-turbo'
MODEL_ID = 'gpt-3.5-turbo:20230327'

openai.api_key='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'

def get_answer(question_id: int, question: str, max_tokens: int):
    ans = {
        'answer_id': shortuuid.uuid(),
        'question_id': question_id,
        'model_id': MODEL_ID,
    }
    for _ in range(3):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{
                    'role': 'system',
                    'content': 'You are a helpful assistant.'
                }, {
                    'role': 'user',
                    'content': question,
                }],
                max_tokens=max_tokens,
            )
            ans['text'] = response['choices'][0]['message']['content']
            return ans
        except Exception as e:
            print('[ERROR]', e)
            ans['text'] = '#ERROR#'
            time.sleep(1)
    return ans


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT answer generation.')
    parser.add_argument('-q', '--question')
    parser.add_argument('-o', '--output')
    parser.add_argument('-role-file', '--role-file')
    parser.add_argument('--max-tokens', type=int, default=1024, help='maximum number of tokens produced in the output')
    args = parser.parse_args()

    questions_dict = {}
    with open(os.path.expanduser(args.question)) as f:
        for line in f:
            if not line:
                continue
            q = json.loads(line)
            questions_dict[q['question_id']] = q['text']

    roles_desc = []
    roles_json = json.load(open(args.role_file))
    for key, value in roles_json.items():
        roles_desc.append([key, value])

    for key, role_desc in roles_desc:
        role_human = role_desc['role_human']
        role_ai = role_desc['role_ai']
        role_back = role_desc['background']
        system = "{background}The following is a chat message between {role_a} and {role_b} using English Language. Question and answer,  forbid the output of multiple rounds.\n\nCurrent conversation:\n\n###{history}",
        system = system.format_map(
            {
                'background': role_back,
                'role_a': role_human,
                'role_b': role_ai
            }
        )
        
        answers = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
            futures = []
            for qid, question in questions_dict.items():
                future = executor.submit(get_answer, qid, question, args.max_tokens)
                futures.append(future)

            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                answers.append(future.result())

        answers.sort(key=lambda x: x['question_id'])

    with open(os.path.expanduser(args.output), 'w') as f:
        table = [json.dumps(ans) for ans in answers]
        f.write('\n'.join(table))
