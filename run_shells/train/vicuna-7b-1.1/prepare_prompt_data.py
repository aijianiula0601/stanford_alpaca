import json

f = "/Users/hjh/PycharmProjects/myprjs/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/evals/test_model_dialogues20230608.json"

f_data = json.load(open(f))

new_data = {}

i = 0
for k in f_data:
    i += 1

    new_data[f"prompt_{i}"] = {'background': f_data[k]['prompt'],
                               "role_name": f_data[k]['bot_name']}

save_f = "prompt_data.json"

json.dump(new_data, open(save_f, 'w'))
