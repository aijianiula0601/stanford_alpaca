import argparse
import json
import os
import time

import openai
import tqdm
import ray

import shortuuid
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_API_RETRY = 5
REQ_TIME_GAP = 10

MODEL = 'gpt-3.5-turbo'
MODEL_ID = 'gpt-3.5-turbo:20230327'

openai.api_key='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'

# @ray.remote(num_cpus=1)
def get_eval(sys_prompt, user_prompt: str, max_tokens: int):
    logging.basicConfig(level=logging.INFO)
    for i in range(MAX_API_RETRY):
        try:
            openai.api_key='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'
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{
                    'role': 'system',
                    'content': sys_prompt
                }, {
                    'role': 'user',
                    'content': user_prompt,
                }],
                temperature=0.2,  # TODO: figure out which temperature is best for evaluation
                max_tokens=max_tokens,
            )
            content = response['choices'][0]['message']['content']
            logger.info(content)
            return content
        except Exception as e:
            logger.error(e)
            time.sleep(5)
    logger.error(f'Failed after {MAX_API_RETRY} retries.')
    return 'error'


def parse_score(review):
    try:
        score_pair = review.split('\n')[0]
        score_pair = score_pair.replace(',', ' ')
        sp = score_pair.split(' ')
        if len(sp) == 2:
            return [float(sp[0]), float(sp[1])]
        else:
            raise Exception('Invalid score pair.')
    except Exception as e:
        logger.error(f'{e}\nContent: {review}\n'
                     'You must manually fix the score pair.')
        return [-1, -1]


def gen_prompt(reviewer_jsons, prompt_jsons, background, cat, ques, ans1, ans2):
    # Default to general category (index=0)
    reviewer_idx = 0
    for idx, reviewer in enumerate(reviewer_jsons):
        if reviewer['category'] == cat:
            reviewer_idx = idx
            break
    prompt_id = reviewer_jsons[reviewer_idx]['prompt_id']
    prompt_json = prompt_jsons[prompt_id-1]
    assert prompt_json['prompt_id'] == prompt_id

    sys_prompt = prompt_json['system_prompt']
    prompt_template = prompt_json['prompt_template']
    defaults = prompt_json['defaults']
    prompt = prompt_template.format(question=ques, background=background, answer_1=ans1, answer_2=ans2, **defaults)

    return sys_prompt, prompt, reviewer_idx+1


def get_json_list(file_path):
    file_path = os.path.expanduser(file_path)
    with open(file_path, 'r') as f:
        json_list = []
        for line in f:
            json_list.append(json.loads(line))
        return json_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ChatGPT-based QA evaluation.')
    parser.add_argument('-q', '--question-file')
    parser.add_argument('-c', '--role-file')
    parser.add_argument('-a', '--answer-file-list', nargs='+', default=[])
    parser.add_argument('-p', '--prompt-file')
    parser.add_argument('-r', '--reviewer-file')
    parser.add_argument('-o', '--output-review-file')
    parser.add_argument('--max-tokens', type=int, default=1024, help='maximum number of tokens produced in the output')
    args = parser.parse_args()

    # ray.init()

    question_jsons = get_json_list(args.question_file)
    answer1_jsons = get_json_list(args.answer_file_list[0])
    answer2_jsons = get_json_list(args.answer_file_list[1])
    reviewer_jsons = get_json_list(args.reviewer_file)
    prompt_jsons = json.load(open(args.prompt_file))
    # print(answer2_jsons[0].keys())
    # print(answer1_jsons[0].keys())

    role_jsons = json.load(open(args.role_file))

    # print(len(question_jsons))
    # print(len(answer2_jsons[0]['无脑的高中女生']))
    # check if # of questions, answers are the same
    # assert len(question_jsons) == len(answer1_jsons) == len(answer2_jsons)

    question_jsons = question_jsons
    total_log = []
    handles = []
    total_jsons = {}
    total_len = len(question_jsons)
    question_idx_list = list(range(total_len))
    for role, role_desc in list(role_jsons.items()):
        answer1_jsons_role = answer1_jsons[0][role]
        answer2_jsons_role = answer2_jsons[0][role]
        review_jsons = []
        reviews = []
        for i in question_idx_list:
            assert answer1_jsons_role[i]['question_id'] == question_jsons[i]['question_id'] == answer2_jsons_role[i]['question_id']
            ques = question_jsons[i]['text']
            cat = question_jsons[i]['category']
            ans1 = answer1_jsons_role[i]['text']
            ans2 = answer2_jsons_role[i]['text']
            # import ipdb; ipdb.set_trace()
            sys_prompt, prompt, reviewer_id = gen_prompt(reviewer_jsons, prompt_jsons, role_desc['background'], cat, ques, ans1, ans2)
            review_id = shortuuid.uuid()
            review_jsons.append({
                'review_id': review_id,
                'question_id': question_jsons[i]['question_id'],
                'answer1_id': answer1_jsons_role[i]['answer_id'],
                'answer2_id': answer2_jsons_role[i]['answer_id'],
                'reviewer_id': reviewer_id,
                'metadata': {},
            })
            # To avoid the rate limit set by OpenAI
            # handles.append(get_eval(sys_prompt, prompt, args.max_tokens))
            eval_result = get_eval(sys_prompt, prompt, args.max_tokens)
            total_log.append([sys_prompt, prompt, eval_result])
            reviews.append(get_eval(sys_prompt, prompt, args.max_tokens))
            logger.info(f'Waiting for {REQ_TIME_GAP} seconds before sending the next request.')
            time.sleep(20)
        # reviews = ray.get(handles)
        for idx, review in enumerate(reviews):
            scores = parse_score(review)
            review_jsons[idx]['text'] = review
            review_jsons[idx]['score'] = scores
        total_jsons[role] = review_jsons.copy()
    with open(f'{args.output_review_file}', 'w') as output_review_file:
        json.dump(total_jsons, output_review_file)
    
    with open('total_log.json', 'w') as f:
        json.dump(total_log, f)