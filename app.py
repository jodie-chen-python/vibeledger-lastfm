# app.py
# C｜Reporter（請自行實作：Streamlit）
#
# 目標：
# - 做一個最小可 Demo 的 Streamlit 儀表板
# - 顯示本週摘要 + Top tracks 表格
#
# 資料讀取規則（避免互等）
# - 優先讀 out/（真資料）
# - 如果 out/ 還沒有，就讀 sample/（讓你不用等 B）
#
# 你需要讀的檔案
# - summary：out/summary.csv 或 sample/summary.sample.csv
# - top tracks：out/top_tracks.csv 或 sample/top_tracks.sample.csv
#
# UI 最小需求（MVP）
# 1) st.title：顯示「VibeLedger｜歌單心電圖」
# 2) 三個 st.metric：
#    - 本週收聽數（scrobble_count）
#    - Top Artist（top_artist）
#    - Top Track（top_track）
# 3) st.dataframe：顯示 Top tracks（前 10）
#
# 建議做法（但你可以用自己的方式）
# - 用 pathlib.Path 檢查 out/ 檔案是否存在，不存在就改讀 sample/
# - 用 pandas.read_csv 讀檔
# - summary.csv 只有 1 行：用 df.iloc[0] 拿到那一行的資料
#
# 你可以使用的套件（看你要不要用）
# - streamlit as st
# - pandas as pd
# - pathlib.Path
#
# 完成後請確保：
# - streamlit run app.py 可以順利啟動
# - 就算 out/ 還沒有，也能用 sample/ 跑出畫面


from pathlib import Path
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="VibeLedger｜歌單心電圖", layout="wide")

# 資料讀取函式
def load_csv(out_path:str, sample_path:str) -> pd.DataFrame:

    out_file = Path(out_path)
    sample_file = Path(sample_path)

    if out_file.exists():
        return pd.read_csv(out_file)
    else:
        return pd.read_csv(sample_file)

# 讀取資料
summary_df = load_csv(
    "out/summary.csv",
    "sample/summary.sample.csv"
)

top_tracks_df = load_csv(
    "out/top_tracks.csv",
    "sample/top_tracks.sample.csv"
)

top_tags_df = load_csv(
    "out/top_tags.csv",
    "sample/top_tags.sample.csv"
)
# UI
st.markdown(
    """
    <style>
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("VibeLedger｜歌單心電圖")
st.subheader("用聽歌紀錄讀懂一週的音樂狀態")
summary = summary_df.iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="本週收聽數",
    value=int(summary["scrobble_count"])
)
col2.metric(
    label="最常收聽藝人",
    value=summary["top_artist"]
)
col3.metric(
    label="最常播放歌曲",
    value=summary["top_track"]
)

col_tracks, col_tags= st.columns(2)
with col_tracks:
    st.subheader("🎧 本週播放排行榜")
    top_tracks = top_tracks_df.rename(columns={
    "rank": "排名",
    "artist": "藝人",
    "track": "歌曲",
    "play_count": "播放次數"
    })

    st.dataframe(
        top_tracks,
        width="stretch", height="content",
        hide_index=True
    )

with col_tags:
    st.subheader("🎶 本週常見音樂標籤")
    top_tags = list(top_tags_df.columns)
    TAG_COLORS = [
        "#ffd6a5",
        "#caffbf",
        "#bdb2ff",
        "#9bf6ff",
        "#ffc6ff",
        "#fdffb6",
    ]

    tag_html = ""

    for i, tag in enumerate(top_tags):
        color = TAG_COLORS[i % len(TAG_COLORS)]

        tag_html += f"""
        <span style="
            display: inline-block;
            margin: 6px 3px 6px 0;
            padding: 6px 14px;
            border-radius: 999px;
            background-color: {color};
            font-size: 15px;
            ">
            {tag}
        </span>
        """
    st.markdown(tag_html, unsafe_allow_html=True)
    st.caption('''
    資料來源：Last.fm \n
    分析區間：最近 7 天
    ''')