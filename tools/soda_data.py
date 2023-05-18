import pandas as pd

# Load a single Parquet file
df = pd.read_parquet("/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/soda/train.parquet")

# Load multiple Parquet files in a directory
# print(df)
# print(df)
selected_columns = ['narrative', 'dialogue', 'speakers']
df_selected = df[selected_columns]

res = []
length_list = []
from tqdm import tqdm
for index, row in tqdm(df_selected.iterrows()):
    # 'index'是当前行的索引，'row'是当前行的数据
    tmp_list, tmp_list_speak, tmp_narrative =  row['dialogue'], row['speakers'], row['narrative']
    long_str = " ".join(tmp_list)
    mean_sen_len = len(long_str.strip(" ")) / len(tmp_list)
    length_list.append(mean_sen_len)

    length_speak = len(tmp_list_speak)
    # if length_speak <= 8 or len(tmp_list) != length_speak or mean_sen_len < 60:
    if length_speak <= 8 or len(tmp_list) != length_speak or mean_sen_len < 80: #120k
    # if length_speak <= 7 or len(tmp_list) != length_speak or mean_sen_len < 70:
        continue

    name_a, name_b = tmp_list_speak[0], tmp_list_speak[1]
    if name_a == name_b:
        continue

    should_str = " ".join([name_a,name_b] * int(length_speak/2))
    real_str = " ".join(tmp_list_speak[:2*int(length_speak/2)])
    if should_str != real_str:
        continue
    elif tmp_list_speak[-1] == tmp_list_speak[-2]:
        continue
    else:
        tmp_res_list = []
        if len(set(tmp_list_speak)) == 2:
            # name_list = list(set(tmp_list_speak))
            name_a, name_b = tmp_list_speak[0], tmp_list_speak[1]
            for ind in range(len(tmp_list_speak)):
                if tmp_list_speak[ind] == name_a:
                    if ind != 0 :
                        tmp_res_list.append({'from': name_a, 'value': tmp_list[ind]})
                    else:
                        tmp_res_list.append({'narrative': tmp_narrative, 'from': name_a, 'value': tmp_list[ind]})
                else:
                    tmp_res_list.append({'from': name_b, 'value': tmp_list[ind]})
            res.append(tmp_res_list)


import statistics
mean = statistics.mean(length_list)
print("Mean:", mean)

# 计算中位数
median = statistics.median(length_list)
print("Median:", median)
# 计算众数
mode = statistics.mode(length_list)
print("Mode:", mode)

print(len(res))
print(len(df_selected))

import json
with open('/mnt/cephfs/zhuchengqi/git/LLM/bigo_stanford_alpaca/datasets/soda_train_name_more.json', 'w') as f:
    json.dump(res, f)

                    



            







            # print(tmp_list_speak)
        # name_a, name_b = tmp_list_speak[0],tmp_list_speak[1]
        # for ind in range(len(tmp_list_speak)):
        #     if ind % 2 == 0:
        #         if tmp_list_speak[ind] != name_a:
        #             print("ERROR",tmp_list_speak,tmp_list)
        #     else:
        #         if tmp_list_speak[ind] != name_b:
        #             print("ERROR",tmp_list_speak,tmp_list)        



