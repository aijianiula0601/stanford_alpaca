from util import get_gpt4_result, get_gpt35_result
import xlwt

import config
#
# prompt = config.place2en_prompt.format_map({"place_name": "中国"})
#
# res = get_gpt4_result(prompt=prompt)
# print(res)

import xlrd
import pandas as pd

if __name__ == '__main__':

    workbook = xlwt.Workbook(encoding="utf-8")  # 实例化book对象
    sheet = workbook.add_sheet("景点名")  # 生成sheet

    # ------------------
    # 写入标题
    # ------------------
    for col, column in enumerate(["国家", "国家-en", "景点名", "景点名-en"]):
        sheet.write(0, col, column)

    # -------------------
    # 数据
    # -------------------
    input_file_name = "ai宠物国家景点名中英文20231221.xls"
    df = pd.read_excel(input_file_name)

    # 打印读取的数据
    data_list = []
    i = 0
    for index, row in df.iterrows():
        country = row["图片路径"]
        place_name = row["以前文案"]
        country_en = row['中文文案']
        place_name_en = row['英文文案']

        data_list.append([country, country_en, place_name, place_name_en])
        i += 1
        if i % 20 == 0:
            print(i)

    print(f"一共数据行数:{len(data_list)}")
    # -------------------
    # 写入每一行
    # -------------------
    for row, data in enumerate(data_list):
        for col, col_data in enumerate(data):
            sheet.write(row + 1, col, col_data)

    workbook.save("/Users/jiahong/Downloads/ai宠物国家景点名中英文20231221.xls")
