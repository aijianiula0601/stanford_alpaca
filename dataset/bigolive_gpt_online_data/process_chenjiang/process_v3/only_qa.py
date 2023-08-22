import json
from tqdm import tqdm

base_dir = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3"

org_f = f"{base_dir}/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial.txt"
save_f = "/tmp/gpt4to_colloquial.txt"

turn_n_list = []
turn_n_dic = {}

with open(save_f, 'w') as fw:
    with open(org_f) as fr:
        for line in tqdm(fr.readlines()):
            example = json.loads(line)

            turn_n = len(example['qas'])
            turn_n_list.append(turn_n)
            turn_n_dic[turn_n] = turn_n_dic.get(turn_n, 0) + 1

            if turn_n < 3:
                continue

            del example['prompt_info']
            del example['background']
            for i in range(len(example["qas"])):
                qa = example['qas'][f'turn_{i}']
                del qa['history']
                del qa['context_send_to_gpt']

            fw.write(f"{json.dumps(example)}\n")

print(f"save to:{save_f}")

save_turn_n_f = "/tmp/turn_n.json"
json.dump(turn_n_list, open(save_turn_n_f, 'w'))
print("轮次保存文件:", save_turn_n_f)

print("轮次对应的对话个数：")
for i in range(0, 10):
    print(f"turn_n:{i},num:{turn_n_dic.get(i, None)}")
