import pandas as pd
import requests
import time

# 指定要读取的 Excel 文件的路径
file_path = '/data/projects/congcong-ai/assets/20240723.xlsx'

# 使用 pandas 读取 Excel 文件
xls = pd.ExcelFile(file_path)

# 遍历每个 sheet
for sheet_name in xls.sheet_names:
    # 读取当前 sheet 的内容
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # 打印每一行的内容
    for index, row in df.iterrows():
        data: dict = row.to_dict()
        if "名称" in data.keys():
            title = data['名称']
        elif "标题" in data.keys():
            title = data['标题']
        if "图片" in data.keys():
            pic = data['图片']
        elif "图标" in data.keys():
            pic = data['图标']
        body = {
            "type": "update",
            "data": [{
                'id': data['主键id'],
                'pic': pic,
                'title': title,
                'path': data['小程序路径'],
                'keyword': "",
                'location': sheet_name
            }]
        }
        print(body)
        res = requests.post(url="http://125.75.69.37:3200/congcong/dataset",
                    json=body).json()
        print(res)
        time.sleep(1)
