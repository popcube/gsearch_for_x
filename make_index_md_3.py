import csv, sys
from datetime import datetime, timezone, timedelta
# import re
import pandas as pd
from get_event_table import get_event_table, get_stream_table

weekday_ja = ["日", "月", "火", "水", "木", "金", "土"]

def entry_format(in_dt, body):
  # format change from ISO YYYY-mm-ddTHH:MM:SS to mm/dd（曜日） HH:MM
  row_0_txt = in_dt.strftime("%m/%d（") + weekday_ja[in_dt.weekday()] + in_dt.strftime("） %H:%M")
  return f"\n---\n\n**DATE**: {row_0_txt}{body}"

def decorate_row(row):
  
  row_0_url = f'https://twitter.com/pj_sekai/status/{row["POST ID"]}'
  row_2 = f'[{row["BODY TEXT"][:5]}...]({row_0_url})'
  
  # # extract the strings that start with http or https and end with whitespace, line break or end of text
  # # then replace them to [LINK](url) format
  # row_2 = re.sub(r"(https?://[^\s]+)(?=\s|$)", r"[LINK](\1)", row[2])
  # # replace all consecutive whitespace and line break to single whitespace
  # row_2 = re.sub(r"\s+", " ", row_2)
  
  # return f"\n---\n\n**DATE**: {row_0}\n<br>\n{row_2}"
  return entry_format(row["POST DATE"], "\n<br>\n" + row_2)

def decorate_row_widget(row):
  row_0_url = f'https://twitter.com/pj_sekai/status/{row["POST ID"]}'
  # row_0 = f'[{row_0_txt}]({row_0_url})'
  
  # use twitter widget
  row_2 = f'<blockquote class="twitter-tweet">\n<a href="{row_0_url}"></a>\n</blockquote>'
  
  return entry_format(row["POST DATE"], "\n<br>\n" + row_2)

def decorate_supplement(row):
  return entry_format(row.iat[0], " 「**" + row.iat[1] + "**」")
  # print(row)
  # sys.exit(19)
  

def main():

  res = []
  res.append("")
  res.append("## プロセカX(旧Twitter) 投稿記録")
  res.append("### 最終更新：" + datetime.now(timezone(timedelta(hours=+9), 'JST')).strftime("%Y/%m/%d %H:%M"))
  res.append("")
  
  # header
  # POST DATE,POST ID,BODY TEXT,DETECTED DATE
  raw_post_table = pd.read_csv("./docs/sorted_data.csv",
                   parse_dates=["POST DATE"],
                   date_format="ISO8601")
  
  # get the oldest  and lastest POST DATE as data cutoff
  oldest_date = raw_post_table.iloc[-1]["POST DATE"]
  latest_date = raw_post_table.loc[0, "POST DATE"]
  
  # create new empty column
  raw_post_table["text"] = ""
  # up to row 4, total 5 rows have widgets (loc assignment includes the assigned index too)
  raw_post_table.loc[:4, "text"] = raw_post_table.loc[:4].apply(decorate_row_widget, axis='columns')
  raw_post_table.loc[5:, "text"] = raw_post_table.loc[5:].apply(decorate_row, axis='columns')
  post_table = raw_post_table[["POST DATE", "text"]]
  post_table.set_index("POST DATE", inplace=True)
  
  event_table = get_event_table()
  stream_table = get_stream_table()
  
  event_start_table = event_table[["開始日", "イベント名"]]
  event_start_table["text"] = event_start_table.apply(decorate_supplement, axis='columns')
  event_start_table.set_index("開始日", inplace=True)
  event_start_table.loc[:, "text"] = event_start_table["text"].apply(lambda x: "イベント " + x + " 開始")
  event_end_table = event_table[["終了日", "イベント名"]]
  event_end_table["text"] = event_end_table.apply(decorate_supplement, axis='columns')
  event_end_table.set_index("終了日", inplace=True)
  event_end_table.loc[:, "text"] = event_end_table["text"].apply(lambda x: "イベント " + x + " 終了")
  
  stream_table = stream_table[["配信日時", "No"]]
  stream_table["text"] = stream_table.apply(decorate_supplement, axis='columns')
  stream_table.set_index("配信日時", inplace=True)
  stream_table.loc[:, "text"] = stream_table["text"].apply(lambda x: x + " 放送開始")
  
  res_table = pd.concat([post_table, event_start_table, event_end_table, stream_table])
  
  # date cutoff
  res_table = res_table[(latest_date >= res_table.index) & (res_table.index >= oldest_date)]
  
  res_table.sort_index(inplace=True, ascending=False)
  
  print(res_table)
  
  res += res_table["text"].to_list()
  
  # res_table["text"].apply(lambda x: x.replace("\n", " ")).to_csv("testoutput.csv")
  
  # sys.exit(1)
    
  res.append("")
  res.append('<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>')
      
  with open(
    "./docs/index.md", "w",
    encoding='utf-8',
    errors='ignore'
  ) as f:
    f.writelines(r + "\n" for r in res)
    
if __name__ == '__main__':
  main()