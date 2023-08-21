import json
from tqdm import tqdm

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3"

org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial.txt"
save_f = "/tmp/gpt4to_colloquial.txt"

with open(save_f, 'w') as fw:
    with open(org_f) as fr:
        for line in tqdm(fr.readlines()):
            example = json.loads(line)

            del example['prompt_info']
            del example['background']
            for i in range(len(example["qas"])):
                qa = example['qas'][f'turn_{i}']
                del qa['history']
                del qa['context_send_to_gpt']

            fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_f}")
