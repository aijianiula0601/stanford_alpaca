import json
from tqdm import tqdm
from joblib import Parallel, delayed
from pathlib import Path

PROMPT_DICT = {
    "background_chat": (
        "The following is the background now give you the background, according to the background, generate the answer to the corresponding question, do not generate multiple rounds of reply.\n"
        "{background}\n"
        "Here is a conversation between {role_a} and {role_b}\n"
        "{history}"
    ),
    "no_background_chat": (
        "Here is a conversation between {role_a} and {role_b}, do not generate multiple rounds of reply.\n"
        "{history}"
    )
}


def get_qa(data_dic={}):
    instruct_list = []
    story = data_dic['story']
    questions = data_dic['questions']
    answers = data_dic['answers']

    for q, a in zip(questions, answers):
        q_input_text = q['input_text']
        a_input_text = a['input_text']

        assert q['turn_id'] == a['turn_id'], f"error turn_id for q-a: {q['turn_id']} != {a['turn_id']}"

        instruct_list.append({"background": story, "question": q_input_text, "answer": a_input_text})

    return instruct_list


base_dir = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/coqa"
train_f = f"{base_dir}/coqa-train-v1.0.json"
dev_f = f"{base_dir}/coqa-dev-v1.0.json"
org_f_list = [train_f, dev_f]

for org_f in org_f_list:
    f_data = json.load(open(org_f))

    example_list = []
    results = Parallel(n_jobs=16, backend="multiprocessing")(
        delayed(get_qa)(example) for example in tqdm(f_data['data']))
    for res in results:
        example_list += res

    save_f = f"{base_dir}/processed_{Path(org_f).name}"

    json.dump(example_list, fp=open(save_f, "w", encoding="utf-8"))
    print(f"save to:{save_f}")
    print(f"example:\n{json.dumps(example_list[0])}")
    print("-" * 100)
