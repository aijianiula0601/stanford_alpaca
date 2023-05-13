import sys
import json

# org_file="/mnt/cephfs/hjh/common_dataset/nlp/qa/en/sex_novel_rewrite/sex_data_processed_05_09.txt"


org_file = "/Users/jiahong/Downloads/sex_data_processed_05_09.txt"

all_n = 0
names_gt3_n = 0
with open(org_file, 'r', encoding='utf-8') as fr:
    for line in fr.readlines():
        line_seg = line.split("###")
        background = line_seg[0]
        chat_names_set = set()
        all_n += 1

        chat_group_contents = [line_seg[1:][i:i + 2] for i in range(0, len(line_seg[1:]), 2)]
        for turn_i, cur_group in enumerate(chat_group_contents):
            for item in cur_group:
                try:
                    item_split = item.split(":")
                    chat_name = item_split[0]
                    chat_content = item_split[1].strip()
                    chat_names_set.add(chat_name)
                except Exception as e:
                    # print(e, f"Error item:{line}")
                    print(item)
                    print('-' * 100)
                    for dd in chat_group_contents:
                        print(dd)
                    sys.exit(1)

        if len(chat_names_set) > 2:
            names_gt3_n += 1

print(f"all:{all_n},names_gt4:{names_gt3_n}")
