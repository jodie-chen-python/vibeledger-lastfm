# VibeLedger｜歌單心電圖（Last.fm）

我們做一個「個人歌單週報」：
輸入 Last.fm 帳號（或使用 sample 資料），抓近 7 天收聽紀錄，產出本週摘要與排行榜，最後用 Streamlit 做成可 Demo 的簡單儀表板。

---

## 專案分工

* A｜Fetcher：抓資料 → 產出 `out/week_data.json`
* B｜Analyzer：算摘要/排行 → 產出 `out/summary.csv`、`out/top_tracks.csv`
* C｜Reporter：做 Streamlit → 讀 `out/summary.csv`、`out/top_tracks.csv`


---

## Repo 結構（照這個建立）

```
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
```

---

## 安裝

建議使用虛擬環境（可選），至少要能跑 Python 3.10+。

```bash
pip install -r requirements.txt
```

`requirements.txt` 建議先放這些（最小可跑）：

* requests
* python-dotenv
* pandas
* streamlit
* matplotlib

---

## 環境變數（只有 A 需要）

在專案根目錄建立 `.env`（不要上傳 GitHub）：

```
LASTFM_API_KEY=你的_lastfm_api_key
LASTFM_USER=你的_lastfm_username
```

---

## 執行順序（Demo 就照這個）

```bash
python fetch.py
python analyze.py
streamlit run app.py
```

---

## Week 1 最小目標

Week 1 只要做到這三件事就算成功：

1. A 能產出 `out/week_data.json`（只要有 scrobbles）
2. B 能產出 `out/summary.csv` 與 `out/top_tracks.csv`
3. C 的 Streamlit 能顯示摘要＋Top tracks 表格

---

## 極簡 I/O 合約（新手版，只留必要欄位）【Last.fm 版】

### 先釘住一個觀念（很重要）
我們 `out/` 內的檔案格式是**我們自己定的乾淨格式**，不等於 Last.fm API 原始回傳。  
原因：Last.fm 回傳資料巢狀、欄位可能缺（例如 now playing 可能沒有時間），直接用會很容易踩雷。  
所以：

- **A 的工作**：把 Last.fm 原始回傳「整理成我們的格式」
- **B/C 的規則**：只讀 `out/` 的乾淨欄位，不需要研究 API 結構
- **raw/**：只給 A 放原始回傳用來 debug，B/C 不讀、也不依賴

---

## A → B：`out/week_data.json`

### A 的 `fetch.py` 要產出 `out/week_data.json`，至少包含：
- `user.username`
- `range.from_ts`、`range.to_ts`
- `scrobbles[]` 每筆至少有：
  - `ts`（UTC timestamp int）
  - `artist`（string）
  - `track`（string）
  - `tags`（list[string]，**永遠非空**）

---

## 欄位映射（A 照這個做，不要猜）
從 Last.fm `user.getRecentTracks` 的每筆 track，整理成我們的 `scrobbles[]`：

- `ts` ← `track.date.uts`  
  - 如果沒有 `date.uts`，通常是 now playing，那筆**直接跳過**
- `artist` ← `track.artist.#text`（最後一定要整理成字串）
- `track` ← `track.name`
- `tags` ← 由 A 額外抓（見下一段 Tags 規則）

（可選）  
- `album` ← `track.album.#text`（沒有就空字串）  
- `url` ← `track.url`（沒有就空字串）

---

## Tags 規則（非常重要，新手最常踩雷）
### 1) `tags` 永遠非空
A 會依序嘗試抓 tags（對同一首歌先去重再抓）：

1. `track.getTopTags`（歌曲 tags）  
2. 抓不到則用 `artist.getTopTags`（歌手 tags）  
3. 再抓不到則補上 `["untagged"]` 作為保底

因此 `scrobbles[].tags` **永遠是非空 list**。

### 2) `["untagged"]` 是本地保底（不是 Last.fm 提供）
- `["untagged"]` 不是 Last.fm 原生標籤  
- 作用是：讓資料格式穩定、避免分析流程因空 tags 爆掉  
- **B 做心情/風格分析時必須排除 `["untagged"]`**

---

## raw/ Debug 規則（可選但推薦）
A 可以把原始回傳存一份到 `raw/lastfm_recenttracks.json` 方便對照  
但 B/C 永遠只讀 `out/week_data.json` 的 `scrobbles[]`

---

## B → C：`out/summary.csv`（只有 1 行）
B 的 `analyze.py` 要產出 `out/summary.csv`，至少包含欄位：
- `username`
- `scrobble_count`
- `top_artist`
- `top_track`
- `real_tag_coverage`（新增，**很重要**）

### real_tag_coverage 計算規則
- `real_tag_coverage = (tags != ["untagged"] 的播放數) / (總播放數)`
- 用來告訴大家：心情分析有多少比例是真的基於 tags

---

## B → C：`out/top_tracks.csv`（多行）
B 的 `analyze.py` 要產出 `out/top_tracks.csv`，至少包含欄位：
- `rank`（1,2,3…）
- `artist`
- `track`
- `play_count`

## top_tracks.csv 的 tags_preview 欄位（給 C 做報告更方便）

`tags_preview` 不是 Last.fm 原生欄位，也不是 `week_data.json` 的必填欄位。  
它是 **B 在輸出 `out/top_tracks.csv` 時自行組合的「顯示用欄位」**，讓 C 不用再回頭讀 JSON 就能在報告上呈現這首歌的 vibe。

### 來源
- 來自 `week_data.json` 的 `scrobbles[].tags`（list[string]）

### 生成規則（建議）
- 若 `tags == ["untagged"]` → `tags_preview = "untagged"`
- 否則 → 取前 3 個 tags，用 `|` 串起來  
  - `tags_preview = "|".join(tags[:3])`

### 範例
- `tags = ["alternative", "indie", "rock", "britpop"]`
- `tags_preview = "alternative|indie|rock"`

---

### C 要做什麼
把 B 產出的 CSV 做成「可看得懂的週報」。
（先做最簡單版本：一頁 Streamlit 或一個 report.html 都可以）

---

### C 的輸入（Input）
C **只讀 out/ 的乾淨檔案**，不用研究 Last.fm API。

**優先讀：**
- `out/summary.csv`
- `out/top_tracks.csv`

**如果 out/ 還沒產出（A/B 尚未跑完），就改讀 sample：**
- `sample/summary.sample.csv`
- `sample/top_tracks.sample.csv`

> 讀取規則（務必寫進程式）：  
> 有 `out/*.csv` 就讀 out；沒有就讀 `sample/*.sample.csv`

---

### out/summary.csv（只有 1 行）
至少包含這些欄位（欄位名固定）：

- `username`：本週分析的帳號
- `scrobble_count`：近 7 天總播放次數（= scrobbles 筆數）
- `top_artist`：本週播放最多的 artist（以播放次數計）
- `top_track`：本週播放最多的 track（以播放次數計）
- `tags_preview`：本週常見 tag 預覽（字串；用 `|` 分隔）
  - 來源：B 從 `week_data.json` 的 `tags[]` 統計出來
  - 注意：`untagged` 是我們本機 fallback（不是 Last.fm 回傳）

---

### out/top_tracks.csv（多行）
至少包含這些欄位（欄位名固定）：

- `rank`：1,2,3...
- `artist`
- `track`
- `play_count`
- `tags_preview`（可選但建議）：該曲常見 tag（字串；用 `|` 分隔）
  - 沒有也沒關係，C 先照欄位存在就顯示、不存在就略過即可

---

### C 的輸出（Output）
最少要交付其中一種：

**方案 1｜Streamlit（推薦）**
- `app.py`：執行後可看到頁面（不用輸出檔案也可）
  - 顯示區塊建議：
    1) 本週摘要（username / scrobble_count / top_artist / top_track）
    2) Top Tracks 表格（前 10 名）
    3) tags_preview（本週 tag 預覽）

**方案 2｜HTML 報告（可選）**
- `out/report.html`
  - 同樣三區塊：Summary / Top Tracks / Tags Preview

---

### C 的範圍（避免踩雷）
- C 不要讀 `raw/`（那是 A debug 用）
- C 不要依賴 `.env` / API key
- 只要吃得到 CSV，就能完成 UI


---

## 平行開工規則（不互等）
- C 不需要等 A/B：先用 `sample/*.csv` 做 UI
- B 不需要等 A：也可以先用 sample 檔寫統計流程
- A 做出真實 `out/week_data.json` 後，再讓 B/C 切換讀 `out/`

---

## 上傳/不上傳規則（避免出事）
### ❌ 這些不要上傳 GitHub
- `.env`（API key/帳號）
- `raw/`（原始回應、tags 快取）
- `out/`（個人聽歌資料）
- `.venv/`（虛擬環境）

### ✅ 這些要上傳 GitHub（團隊共同開發）
- `fetch.py / analyze.py / app.py`
- `sample/`
- `README.md`
- `requirements.txt`
- `.gitignore`


---

## Reference

Last.fm API

* [https://www.last.fm/api](https://www.last.fm/api)
* [https://www.last.fm/api/show/user.getRecentTracks](https://www.last.fm/api/show/user.getRecentTracks)
* [https://www.last.fm/api/show/artist.getTopTags](https://www.last.fm/api/show/artist.getTopTags)

Streamlit / pandas / matplotlib

* [https://docs.streamlit.io/](https://docs.streamlit.io/)
* [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
* [https://matplotlib.org/stable/api/pyplot_summary.html](https://matplotlib.org/stable/api/pyplot_summary.html)
