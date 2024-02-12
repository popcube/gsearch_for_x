import pandas as pd
import requests
from datetime import datetime

import sys


def unit_name_convert(in_str):
    if in_str == "0_VS":
        return "vs"
    elif in_str == "1_L/n":
        return "l/n"
    elif in_str == "2_MMJ":
        return "mmj"
    elif in_str == "3_VBS":
        return "vbs"
    elif in_str == "4_WxS":
        return "wxs"
    elif in_str == "5_25":
        return "n25"
    elif in_str == "混合":
        return "mix"
    else:
        print("unrecognized event type", in_str)
        sys.exit(1)


def date_convert(in_str, start=False, end=False):
    if start:
        return datetime.strptime(in_str + "T15", f"%Y/%m/%dT%H")
    elif end:
        return datetime.strptime(in_str + "T21", f"%Y/%m/%dT%H")
    else:
        return datetime.strptime(in_str, f"%Y/%m/%d")


def get_event_table():
    pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")
    if pjsekai_res.ok:

        a = pd.read_html(pjsekai_res.content, index_col='No', encoding="utf-8",
                        attrs={"id": "sortable_table1"})[0]
        # default columns belown
        # No, 週目, イベント名, 形式, ユニット, タイプ, 書き下ろし楽曲, 開始日, 終了日, 日数, 参加人数
        
        a["ユニット"] = a["ユニット"].apply(unit_name_convert)
        a["開始日"] = a["開始日"].apply(date_convert, start=True)
        a["終了日"] = a["終了日"].apply(date_convert, end=True)
        
        # one event started with delay due to extended maintenance
        a.loc[120, "開始日"] = datetime(2024, 1, 31, 20)
        
        # a.to_csv("./event_data.csv", index=False, header=False)
        return a


def get_stream_table():
    pjsekai_res = requests.get("https://pjsekai.com/?1c5f55649f")
    if pjsekai_res.ok:
        a = pd.read_html(pjsekai_res.content, 
                     encoding="utf-8",
                     attrs={"border": "0", "cellspacing": "1", "class": "style_table"})
        # print(a[0])

        a_temp = a[0][["No", "配信日時"]]
        a_temp.columns = ["No", "配信日時"]
        # print(a_temp)
        a_temp = a_temp.drop_duplicates(ignore_index=True)

        # convert Japanese datetime string to datetime object
        a_temp["配信日時"] = a_temp["配信日時"].apply(
            lambda x: datetime.strptime(x[:x.index("(")], "%Y/%m/%d"))
        a_temp.loc[:, "No"] = a_temp["No"].apply(lambda x: "プロセカ放送局 " + x)

        # Be careful that No column includes the description of the stream
        return a

test_table = get_stream_table()
# print(test_table)