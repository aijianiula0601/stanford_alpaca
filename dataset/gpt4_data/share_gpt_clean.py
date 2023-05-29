import json
from tqdm import tqdm

# ------------------------------------------------------------
# 清理俊士没清理好的数据
# ------------------------------------------------------------
# org_f = "/mnt/cephfs/liujunshi/Projects/bigo_stanford_alpaca/datasets/gpt4_shared_data.json"
org_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt/ShareGPT_V3_unfiltered_cleaned_split.json"

print(f"----lem:{len(json.load(open(org_f)))}")


# save_f = "/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sharegpt/cleaned_gpt4_shared_data.json"
#
# human_name = "human"
# from_key = "from"
# value_key = "value"
#
# filter_words_list = ["Product((Product))", "AI language model"]
#
# new_data_list = []
#
# all_n = 0
# skip_n = 0
# for example in tqdm(json.load(open(org_f))):
#     all_n += 1
#     skip_flag = False
#     for i, qa in enumerate(example):
#         # ---------------------------------
#         # 1.过滤第一个问题不是human的对话
#         # ---------------------------------
#         if i == 0 and qa[from_key] != human_name:
#             skip_n += 1
#             skip_flag = True
#             break
#         # ---------------------------------
#         # 2.过滤在value中存在关键词的对话
#         # ---------------------------------
#         w_flag = False
#         for w in filter_words_list:
#             if w.lower() in qa[value_key].lower():
#                 skip_n += 1
#                 skip_flag = True
#                 w_flag = True
#                 break
#         if w_flag:
#             break
#     if skip_flag:
#         continue
#     new_data_list.append(example)
#
# print(f"all_n:{all_n},skill_n:{skip_n},exist_n:{all_n - skip_n}")
# json.dump(new_data_list, open(save_f, 'w'))
# print(f"exmplas:{len(new_data_list)},save to:{save_f}")
