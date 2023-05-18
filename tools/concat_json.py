import json
import random

# chat_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/soda_train_name_more.json"
chat_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/soda_train_name.json"
orign_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/gpt4_shared_data.json"
live_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/live0512_filter1.json"
sexy_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/sexy_840_12.json"

save_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/gpt4_sodatrain_live4w_sexy12.json"
# save_json = "/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/gpt4_sodatrain_name_30w.json"

gpt_4_data_dirt = json.load(open(orign_json))
gpt_4_data = []
for tmp_list in gpt_4_data_dirt:
    if len(tmp_list) > 2:
        gpt_4_data.append(tmp_list)

chat_data = json.load(open(chat_json))
sexy_data = json.load(open(sexy_json))

live_data_total = json.load(open(live_json))
random.shuffle(live_data_total)
random.shuffle(live_data_total)
live_data = []
for ind in range(40000):
    live_data.append(live_data_total[ind])


#gpt 数据扩充三倍
# total_list = gpt_4_data + chat_data + gpt_4_data + gpt_4_data
total_list = gpt_4_data + chat_data + live_data + sexy_data

random.shuffle(total_list)
random.shuffle(total_list)

with open(save_json, 'w') as f:
    json.dump(total_list, f)
