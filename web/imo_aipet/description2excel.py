import xlwt
import os
from pathlib import Path
import random
from tqdm import tqdm

workbook = xlwt.Workbook(encoding="utf-8")  # 实例化book对象
sheet = workbook.add_sheet("文案内容")  # 生成sheet

# ------------------
# 写入标题
# ------------------
for col, column in enumerate(["图片路径", "中文文案", "英文文案"]):
    sheet.write(0, col, column)

# -------------------
# 数据
# -------------------

base_dir = "/mnt/cephfs/hjh/train_record/images/dataset/imo_aipet/region/"
data_dir = f"{base_dir}/20231219/journey_imgs"
description_data_list = []

f_list = [f for f in Path(data_dir).rglob("new_description.txt")]

# 采样
sample_n = min([1000, len(f_list)])
sample_f_list = random.sample(f_list, k=sample_n)

for org_f in tqdm(sample_f_list):
    desc_f = str(org_f)
    desc_en_f = desc_f.replace(".txt", "_en.txt")
    f_path = str(org_f.parent).replace(base_dir, '')

    if os.path.exists(desc_f) and os.path.exists(desc_en_f):
        desc_txt = open(desc_f, 'r').read()
        desc_en_txt = open(desc_en_f, 'r').read()
        description_data_list.append([f_path, desc_txt, desc_en_txt])

print(f"description_data_list len:{len(description_data_list)}")

# -------------------
# 写入每一行
# -------------------
for row, data in enumerate(description_data_list):
    for col, col_data in enumerate(data):
        sheet.write(row + 1, col, col_data)

workbook.save("文案示例20231221.xls")
