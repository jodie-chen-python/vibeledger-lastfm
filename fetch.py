"""
fetch.py
A｜Fetcher
目標：產出 out/week_data.json（乾淨格式）
Week 1：先能產檔即可；若尚未接 API，會產出 demo 資料讓後面流程能跑。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


OUT_DIR = Path("out")
RAW_DIR = Path("raw")


def now_utc_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def demo_week_data(username: str) -> dict:
    # 產出 10 筆 demo scrobbles，讓 analyze/app 能先跑起來
    now = now_utc_ts()
    scrobbles = []
    for i in range(10):
        scrobbles.append(
            {
                "ts": now - i * 3600,
                "artist": "Radiohead",
                "track": f"Demo Track {i+1}",
            }
        )

    return {
        "user": {"username": username},
        "range": {"from_ts": now - 7 * 24 * 3600, "to_ts": now},
        "scrobbles": scrobbles,
    }


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    RAW_DIR.mkdir(exist_ok=True)

    username = os.getenv("LASTFM_USER", "demo_user")

    # TODO(A): Week 1 接 Last.fm 時，把 demo_week_data 換成真正抓到的 scrobbles
    data = demo_week_data(username=username)

    out_path = OUT_DIR / "week_data.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] wrote {out_path}")


if __name__ == "__main__":
    main()
