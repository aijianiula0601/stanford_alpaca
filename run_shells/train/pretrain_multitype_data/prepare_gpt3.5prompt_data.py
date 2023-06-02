import json

# -----------------
# 转换为qa格式
# -----------------
HUMAN_NAME_KEY = "human_name"
BOT_NAME_KEY = "bot_name"
BACKGROUND_KEY = "background"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWER_KEY = "answer"
DATASET_KEY = "dataset_name"
PROMPT_KEY = "prompt"


def trans2qa(all_data, dataset_name):
    new_data = []
    skip_n = 0
    for turns_data in all_data:
        background = None
        prompt=None
        qas = {}
        human_name = turns_data[0]['from']
        bot_name = turns_data[1]['from']
        turn_i = 0

        try:
            for i, td in enumerate(turns_data):
                if i == 0:
                    background = td['background']
                    prompt = td[PROMPT_KEY]
                if (i + 1) % 2 == 1:
                    assert human_name == td['from'], f"error qas:{json.dumps(turns_data)}"
                    qas[f"turn_{turn_i}"] = {QUESTION_KEY: td['value']}
                else:
                    assert bot_name == td['from']
                    qas[f"turn_{turn_i}"][ANSWER_KEY] = td['value'].strip()
                    turn_i += 1
        except Exception as e:
            skip_n += 1
            continue

        turn_n = len(qas)
        if QUESTION_KEY not in qas[f"turn_{turn_n - 1}"] or ANSWER_KEY not in qas[f"turn_{turn_n - 1}"]:
            qas.pop(f"turn_{turn_n - 1}")

        if len(qas) < 1:
            continue

        assert background is not None
        assert prompt is not None
        new_data.append(
            {BACKGROUND_KEY: background,
             PROMPT_KEY: prompt,
             DATASET_KEY: dataset_name, HUMAN_NAME_KEY: human_name, BOT_NAME_KEY: bot_name,
             QAS_KEY: qas})

    print(f"----skip qas nums:{skip_n}")

    return new_data


#--------------------------------
# emoji占比较少的prompt数据
#--------------------------------
# org_f = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data/sexy_chat_prompt_1_2_2020.json"
# save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_gpt3.5sex/gpt3.5sex_data.json"

#--------------------------------
# emoji占比60~79的prompt数据
#--------------------------------
org_f = "/mnt/cephfs/pangyongqiang/proj/LLM/data_fetch/data/sexy_chat_prompt_3_2000_Jamie_check.json"
save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/pretrain_multitype_data/ft2_gpt3.5sex_emoji60%/gpt3.5sex_data.json"


data_list = json.load(open(org_f))
new_data_list = []
for qas in data_list:
    promp = qas[0]['prompt_b']
    for i, qa in enumerate(qas[1:]):
        if i == 0:
            qa[PROMPT_KEY] = promp
            qa[BACKGROUND_KEY] = qa['BACKGROUD_B']
            del qa['BACKGROUD_A']
            del qa['BACKGROUD_B']
        else:
            break
    new_data_list.append(qas[1:])

new_gpt4_sex_data_list = trans2qa(new_data_list, dataset_name="gpt35_sex")
json.dump(new_gpt4_sex_data_list, open(save_f, 'w'))
print(f"save gpt4 sex to:{save_f}")
