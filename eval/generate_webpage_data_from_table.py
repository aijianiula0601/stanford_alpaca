"""Generate json file for webpage."""
import json
import os
import re

models = ['model1', 'model2']


def read_jsonl(path: str, key: str=None):
    data = []
    with open(os.path.expanduser(path)) as f:
        for line in f:
            if not line:
                continue
            data.append(json.loads(line))
    if key is not None:
        data.sort(key=lambda x: x[key])
        data = {item[key]: item for item in data}
    return data


def trim_hanging_lines(s: str, n: int) -> str:
    s = s.strip()
    for _ in range(n):
        s = s.split('\n', 1)[1].strip()
    return s


if __name__ == '__main__':
    # import ipdb; ipdb.set_trace()
    questions = read_jsonl('tables/question.jsonl', key='question_id')

    # model1_answers = read_jsonl('tables/answer.jsonl', key='question_id')
    # model2_answers = read_jsonl('tables/answer.jsonl', key='question_id')
    model1_answers = json.load(open('tables/answer.jsonl'))
    for key, value in model1_answers.items():
        data = {item['question_id']: item for item in value}
        model1_answers[key] = data
    
    model2_answers = json.load(open('tables/answer.jsonl'))
    for key, value in model2_answers.items():
        data = {item['question_id']: item for item in value}
        model2_answers[key] = data
    
    review_data= json.load(open('tables/review_output1.jsonl'))
    for key, value in review_data.items():
        data = {item['question_id']: item for item in value}
        review_data[key] = data
    role_desc = json.load(open('tables/role.json'))

    # review_data = read_jsonl('table/review_output1.jsonl', key='question_id')

    records = []
    for role in review_data.keys():
        for qid in questions.keys():
            r = {
                'id': qid,
                'category': role,
                'question': questions[qid]['text'],
                'answers': {
                    'model1': model1_answers[role][qid]['text'],
                    'model2': model2_answers[role][qid]['text'],
                },
                'evaluations': {
                    'evaluation': review_data[role][qid]['text'],
                },
                'scores': {
                    'scores': review_data[role][qid]['score'],
                },
            }

            # cleanup data
            cleaned_evals = {}
            for k, v in r['evaluations'].items():
                v = v.strip()
                lines = v.split('\n')
                # trim the first line if it's a pair of numbers
                if re.match(r'\d+[, ]+\d+', lines[0]):
                    lines = lines[1:]
                v = '\n'.join(lines)
                cleaned_evals[k] = v.replace('Assistant 1', "**Assistant 1**").replace('Assistant 2', '**Assistant 2**')

            r['evaluations'] = cleaned_evals
            records.append(r)

    # Reorder the records, this is optional
    # for r in records:
    #     if r['id'] <= 20:
    #         r['id'] += 60
    #     else:
    #         r['id'] -= 20
    # for r in records:
    #     if r['id'] <= 50:
    #         r['id'] += 10
    #     elif 50 < r['id'] <= 60:
    #         r['id'] -= 50
    # for r in records:
    #     if r['id'] == 7:
    #         r['id'] = 1
    #     elif r['id'] < 7:
    #         r['id'] += 1 

    # records.sort(key=lambda x: x['id'])

    # Write to file
    with open('webpage/data.json', 'w') as f:
        json.dump({'questions': records, 'models': models, 'roles': role_desc}, f, indent=2)
