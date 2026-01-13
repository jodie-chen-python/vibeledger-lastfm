# analyze.py
# B｜Analyzer（請自行實作）
#
# 目標：
# - 讀取 out/week_data.json
# - 產出 out/summary.csv（1 行摘要）
# - 產出 out/top_tracks.csv（Top tracks 排行）
#
# I/O 合約（你要遵守的輸出欄位）
# 1) out/summary.csv（只有 1 行）
#    欄位：username, scrobble_count, top_artist, top_track
#
# 2) out/top_tracks.csv（多行，至少前 10）
#    欄位：rank, artist, track, play_count
#
# week_data.json 的最小欄位（你要讀這些就好）
# - user.username
# - scrobbles[] 每筆：
#   - ts (int)
#   - artist (str)
#   - track (str)
#
# 建議做法（但你可以用自己的方式）
# - scrobble_count = len(scrobbles)
# - top_artist：統計 artist 出現次數最多者
# - top_track：統計 track 出現次數最多者
# - top_tracks：以 (artist, track) 當 key 統計播放次數，排序後輸出 rank
#
# 注意事項
# - out/week_data.json 可能不存在：請提示先跑 python fetch.py
# - 資料可能有空字串：統計前可先過濾
#
# 你可以使用的套件（看你要不要用）
# - json（讀 JSON）
# - pandas（輸出 csv 比較方便）
# - collections.Counter（做計數很快）
#
# 完成後請確保：
# - python analyze.py 會成功產出 out/summary.csv、out/top_tracks.csv
# - 檔案欄位名稱拼字要完全一致（不要自己改欄位名）
# analyze.py
# B｜Analyzer（請自行實作）
#
# 目標：
# - 讀取 out/week_data.json
# - 產出 out/summary.csv（1 行摘要）
# - 產出 out/top_tracks.csv（Top tracks 排行）
#
# I/O 合約（你要遵守的輸出欄位）
# 1) out/summary.csv（只有 1 行）
#    欄位：username, scrobble_count, top_artist, top_track
#
# 2) out/top_tracks.csv（多行，至少前 10）
#    欄位：rank, artist, track, play_count
#
# week_data.json 的最小欄位（你要讀這些就好）
# - user.username
# - scrobbles[] 每筆：
#   - ts (int)
#   - artist (str)
#   - track (str)
#
# 建議做法（但你可以用自己的方式）
# - scrobble_count = len(scrobbles)
# - top_artist：統計 artist 出現次數最多者
# - top_track：統計 track 出現次數最多者
# - top_tracks：以 (artist, track) 當 key 統計播放次數，排序後輸出 rank
#
# 注意事項
# - out/week_data.json 可能不存在：請提示先跑 python fetch.py
# - 資料可能有空字串：統計前可先過濾
#
# 你可以使用的套件（看你要不要用）
# - json（讀 JSON）
# - pandas（輸出 csv 比較方便）
# - collections.Counter（做計數很快）
#
# 完成後請確保：
# - python analyze.py 會成功產出 out/summary.csv、out/top_tracks.csv
# - 檔案欄位名稱拼字要完全一致（不要自己改欄位名）



# 讀取 out/week_data.json
import json
# from os import path
# root = 'C:/Users/user/Python/ccclub_2025 Fall/vibeledger'
# jsonPath = path.join(root, 'outweek_data.json')
# with open(jsonPath, 'r', encoding="utf-8") as jsonFile: #開檔案
#     # part1 -- summary.sample.csv
#     jsonObj = json.load(jsonFile) #jsonObj存放 讀進來的json物件

import json
import requests

url = "https://raw.githubusercontent.com/jodie-chen-python/vibeledger-lastfm/d1963f27844d765dff6c8ac39a4bbbef45122f17/sample/week_data.sample.json"

resp = requests.get(url)
resp.raise_for_status()

jsonObj = resp.json()

# json可以直接用"索引值"和"key值" 取得資料)
user = jsonObj['user']["username"]
scrobblecnt = len(jsonObj['scrobbles'])
scrobble_info = jsonObj['scrobbles']
print(type(scrobble_info)) # list, 但是裡面裝的元素是dic
print(scrobble_info)

from collections import Counter
# 單純取出所有 artist
artist_list = [item["artist"] for item in jsonObj["scrobbles"]]
artist_counter = Counter(artist_list)
top_artist = artist_counter.most_common(1)[0][0]

# 單純取出所有 track
track_list = [item["track"] for item in jsonObj["scrobbles"]]
track_counter = Counter(track_list)
top_track = track_counter.most_common(1)[0][0]

print(user, scrobblecnt, top_artist, top_track)
print(scrobble_info)


# part2 -- top_tracks.sample.csv

import pandas as pd
df = pd.DataFrame(scrobble_info)
print(df)
track_count = (df
.groupby(["artist", "track"])
.size()
.reset_index(name="play_count")
)

track_count = track_count.sort_values(
by="play_count",
ascending=False
)
track_count["ranking"] = range(1, len(track_count) + 1)

result_df = track_count[
["ranking", "track", "artist", "play_count"]]

print(result_df)




# 產出 out/summary.csv、out/top_tracks.csv
import csv 

# 開啟檔案
with open("sum.csv", mode="w", newline="",encoding="utf-8-sig") as file: #newline="" 才不會在寫入時出現不該出現的東西。

    # 建立Writer物件
    writer = csv.writer(file)

    # (每次)寫入一個列表
    writer.writerow(['username', 'scrobble_count', 'top_artist', 'top_track'])
    writer.writerow([user, scrobblecnt, top_artist, top_track])

with open("top.csv", mode="w", newline="",encoding="utf-8-sig") as file2: #newline="" 才不會在寫入時出現不該出現的東西。

    # 建立Writer物件
    writer2 = csv.writer(file2)

    # (每次)寫入一個列表
    writer2.writerow(['rank','artist','track','play_count'])
    for _, row in result_df.iterrows():
        writer2.writerow([
            row["ranking"],
            row["artist"],
            row["track"],
            row["play_count"]
        ])