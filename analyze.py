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
