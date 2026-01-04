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
