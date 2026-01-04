VibeLedger｜歌單心電圖（Last.fm）｜新手 MVP

我們做一個「個人歌單週報」：
輸入 Last.fm 帳號（或使用 sample 資料），抓近 7 天收聽紀錄，產出本週摘要與排行榜，最後用 Streamlit 做成可 Demo 的簡單儀表板。

專案分工（3 人就能跑）

A｜Fetcher：抓資料 → 產出 out/week_data.json

B｜Analyzer：算摘要/排行 → 產出 out/summary.csv、out/top_tracks.csv

C｜Reporter：做 Streamlit → 讀 out/summary.csv、out/top_tracks.csv

主揪：整合 repo、維護規格、確保大家跑得起來。


Repo 結構（照這個建立）

.

├── fetch.py

├── analyze.py

├── app.py

├── requirements.txt

├── README.md

├── sample/

│   ├── summary.sample.csv

│   └── top_tracks.sample.csv

├── out/                # 程式跑完才會出現，建議不上傳

└── raw/                # Debug 用：A 可放原始 API 回傳（不上傳、B/C 不讀）


安裝

建議使用虛擬環境（可選），至少要能跑 Python 3.10+。

pip install -r requirements.txt


requirements.txt 建議先放這些（最小可跑）：

requests

python-dotenv

pandas

streamlit

matplotlib

環境變數（只有 A 需要）

在專案根目錄建立 .env（不要上傳 GitHub）：

LASTFM_API_KEY=你的_lastfm_api_key
LASTFM_USER=你的_lastfm_username

執行順序（Demo 就照這個）
python fetch.py
python analyze.py
streamlit run app.py

Week 1 最小目標

Week 1 只要做到這三件事就算成功：

A 能產出 out/week_data.json（只要有 scrobbles）

B 能產出 out/summary.csv 與 out/top_tracks.csv

C 的 Streamlit 能顯示摘要＋Top tracks 表格

極簡 I/O 合約

我們 out/ 內的檔案格式是我們自己定的乾淨格式，不等於 Last.fm API 原始回傳。
原因：Last.fm 回傳資料巢狀、欄位有時會缺（例如 now playing 可能沒有時間），直接用會很容易踩雷。
所以：

A 的工作：把 Last.fm 原始回傳「整理成我們的格式」

B/C 的規則：只讀 out/ 的乾淨欄位，不需要研究 API 結構

raw/：只給 A 放原始回傳用來 debug，B/C 不讀、也不依賴

A → B：out/week_data.json

A 的 fetch.py 要產出 out/week_data.json，至少包含：

user.username

range.from_ts、range.to_ts

scrobbles[] 每筆至少有：

ts（UTC timestamp int）

artist（string）

track（string）

欄位映射（A 照這個做，不要猜）

從 Last.fm user.getRecentTracks 的每筆 track，整理成我們的 scrobbles[]：

ts ← track.date.uts
如果沒有 date.uts，通常是 now playing，那筆直接跳過

artist ← track.artist.#text（最後一定要整理成字串）

track ← track.name

（可選）album ← track.album.#text（沒有就空字串）

（可選）url ← track.url（沒有就空字串）

raw/ Debug 規則（可選但推薦）

A 可以把原始回傳存一份到 raw/recent_tracks_raw.json 方便對照

但 B/C 永遠只讀 out/week_data.json 的 scrobbles[]

B → C：out/summary.csv（只有 1 行）

B 的 analyze.py 要產出 out/summary.csv，至少包含欄位：

username

scrobble_count

top_artist

top_track

B → C：out/top_tracks.csv（多行）

B 的 analyze.py 要產出 out/top_tracks.csv，至少包含欄位：

rank（1,2,3…）

artist

track

play_count

平行開工規則（不互等）

C 不需要等 A/B：先用 sample/*.csv 做 UI

B 不需要等 A：也可以先用 sample 檔寫統計流程

A 做出真實 out/week_data.json 後，再讓 B/C 切換讀 out/


Reference

Last.fm API

https://www.last.fm/api

https://www.last.fm/api/show/user.getRecentTracks

https://www.last.fm/api/show/artist.getTopTags

Streamlit / pandas / matplotlib

https://docs.streamlit.io/

https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html

https://matplotlib.org/stable/api/pyplot_summary.html
