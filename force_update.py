import os, sys
from datetime import datetime, timedelta
import json
import csv

from make_index_md_3 import main as make_index_md
from send_to_discord import main as send_to_discord

GITHUB_EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH")

def get_current_data():
  with open(
    "./docs/sorted_data.csv", "r",
    encoding='utf-8',
    errors='ignore'
  ) as f:
    reader = csv.reader(f)
    
    # skip header
    return [r for r in reader][1:]

def datetime_str(dt_str):
  dt = datetime.fromisoformat(dt_str.rstrip("Z")) + timedelta(hours=+9)
  return dt.isoformat()

def post_sort(response):
  sorted_posts = []
  try:
    total_results = response[0]["queries"]["request"][0]["totalResults"]
    print()
    print(f"total results: {total_results}")
    print(f"max page: {max_page}")
    print()

  except Exception as e:
    print(e)
    print("no search results?")
    print()

  else:
    now_str = (datetime.now() + timedelta(hours=9)).isoformat()
    for res in response:
      for item in res["items"]:
        try:
          post_obj = item["pagemap"]["socialmediaposting"][0]
          metatag_body = item["pagemap"]["metatags"][0]["og:description"]
          sorted_posts.append([
            datetime_str(post_obj["datecreated"]),                ## date
            post_obj["identifier"],                               ## id
            # post_obj["articlebody"].rstrip("Translate post"),     ## body
            metatag_body,                                         ## metatag body
            now_str                                               ## detected time
          ])
        except Exception as e:
          print(e)
          print("cannot retrieve info from out.json, skipping")
          pass
          
    sorted_posts.sort(key=lambda x: x[1], reverse=True)

  return sorted_posts


if __name__ == '__main__':
  event_dict = dict()
  with open(GITHUB_EVENT_PATH, "r") as f:
    event_dict = json.loads(f.read())
  retention_days = 94
  
  cur_posts = get_current_data()
  # print(cur_posts)
  
  cutoff_date = datetime.now() + timedelta(days= -1 * retention_days)
  
  ## cut the old data using date criteria
  cur_posts = [post for post in cur_posts
               if datetime.fromisoformat(post[0]) > cutoff_date]
  
  print(**event_dict)
  sys.exit(1)
  new_posts = post_sort(res)
  
  ## all posts including dupe entry
  all_posts = cur_posts + new_posts
  
  cur_ids = [r[1] for r in cur_posts]
  new_ids = list(set([r[1] for r in new_posts]))
  # new post ids that are not in the current list
  added_ids = [id for id in new_ids if id not in cur_ids]
  
  # when new post is detected
  if len(added_ids) > 0:
  # if True:
    
    added_ids.sort(reverse=True)
    send_to_discord(added_ids)
    
    added_posts = []    
    
    print()
    print("########## New posts ##########")
    for post in new_posts:
      ## get only added posts AND unique ids
      if post[1] in added_ids and post[1] not in [post_pre[1] for post_pre in added_posts]:
        added_posts.append(post)
        print(post[:2])
    print()
    
    posts = cur_posts + added_posts
    posts.sort(key=lambda x: x[1], reverse=True)
    
    # add header for output
    posts.insert(0, ["POST DATE", "POST ID", "BODY TEXT", "DETECTED DATE"])
    # post_strs = [",".join(post.values()) + "\n" for post in posts]
    with open(
      "./docs/sorted_data.csv", "w",
      encoding='utf-8',
      errors='ignore'
    ) as f:
      writer = csv.writer(f)
      writer.writerows(posts)
    
    make_index_md()
    
    with open(
      "./sorted_data_viewer.csv", "w",
      encoding='utf-8',
      errors='ignore'
    ) as f:
      writer = csv.writer(f)
      writer.writerows([item.replace("\n", " ") for item in post] for post in posts)
    
    if len(GITHUB_OUTPUT) > 0:
      with open(GITHUB_OUTPUT, "a") as f:
        f.write("CHANGE=YES\n")
  
  else:
    print("No new post detected")
    
    
  
