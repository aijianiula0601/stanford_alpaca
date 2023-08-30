import json
from tqdm import tqdm

org_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial_topic.json"
save_f = "/mnt/cephfs/hjh/train_record/nlp/stanford_alpaca/dataset/bigolive_gpt_online_data/chengjiang_data/v3/topic/bigolive_robot_chat_history.for_train.20230804-20230808.starter_user.v2.en_gpt4to_colloquial_topic.txt"

with open(save_f, 'w') as fw:
    for example in tqdm(json.load(open(org_f))):
        fw.write(f"{json.dumps(example)}\n")


print(f"save to:{save_f}")
