"""
fetch.py
A｜Fetcher

目標：
- 抓 Last.fm 近 7 天 scrobbles，輸出 out/week_data.json
- 同時抓 tags（track tags 優先，抓不到就用 artist tags 當備援）
- 抓 tags 以「不同歌曲」為單位去重，最多抓 100 首（較慢但覆蓋率更高）
- tags 永遠非空：若 Last.fm 抓不到 tags，補上 ["untagged"] 作為保底（非 Last.fm 原生）
- 使用快取 raw/tags_cache.json，避免重複呼叫 API
- 若未設定 .env 或 API 失敗，fallback demo（讓後面流程能跑）

輸出：
- out/week_data.json（乾淨格式 + tags）
- raw/lastfm_recenttracks.json（原始回應，方便 debug）
- raw/tags_cache.json（tag 快取，下次跑更快）

注意：
- ["untagged"] 是我們的保底標籤，Analyzer 做心情計算時請排除它
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from dotenv import load_dotenv


OUT_DIR = Path("out")
RAW_DIR = Path("raw")
TAGS_CACHE_PATH = RAW_DIR / "tags_cache.json"

# 保證 tags 永遠非空的保底標籤（非 Last.fm 原生 tags）
FALLBACK_TAGS = ["untagged"]


def now_utc_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def demo_week_data(username: str) -> dict:
    now = now_utc_ts()
    scrobbles = []
    for i in range(10):
        scrobbles.append(
            {
                "ts": now - i * 3600,
                "artist": "Radiohead",
                "track": f"Demo Track {i+1}",
                "tags": ["demo", "alternative"],
            }
        )

    return {
        "user": {"username": username},
        "range": {"from_ts": now - 7 * 24 * 3600, "to_ts": now},
        "scrobbles": scrobbles,
    }


def safe_track_key(artist: str, track: str) -> str:
    return f"{artist}|||{track}".strip().lower()


def load_tags_cache() -> Dict[str, List[str]]:
    if not TAGS_CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(TAGS_CACHE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_tags_cache(cache: Dict[str, List[str]]) -> None:
    TAGS_CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fetch_recent_tracks_lastfm(api_key: str, username: str, from_ts: int, to_ts: int) -> dict[str, Any]:
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": username,
        "api_key": api_key,
        "format": "json",
        "limit": 200,  # MVP：先抓一頁；之後可加分頁
        "from": from_ts,
        "to": to_ts,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(
            f"Last.fm API error {data.get('error')}: {data.get('message')}"
        )
    return data


def normalize_scrobbles(recenttracks_json: dict[str, Any]) -> List[Dict[str, Any]]:
    tracks = recenttracks_json.get("recenttracks", {}).get("track", [])
    if not isinstance(tracks, list):
        return []

    out: List[Dict[str, Any]] = []
    for t in tracks:
        # 跳過正在播放（通常沒有 date.uts）
        date_obj = t.get("date")
        if not date_obj or "uts" not in date_obj:
            continue

        try:
            ts = int(date_obj["uts"])
        except Exception:
            continue

        artist_obj = t.get("artist")
        if isinstance(artist_obj, dict):
            artist_name = artist_obj.get("#text", "") or ""
        else:
            artist_name = str(artist_obj or "")

        track_name = t.get("name", "") or ""
        if not artist_name or not track_name:
            continue

        out.append({"ts": ts, "artist": artist_name, "track": track_name})

    out.sort(key=lambda x: x["ts"], reverse=True)
    return out


def _extract_top_tag_names(data: dict[str, Any], top_n: int) -> List[str]:
    tags = data.get("toptags", {}).get("tag", [])
    if not tags:
        return []
    if isinstance(tags, dict):
        tags = [tags]

    names: List[str] = []
    for tag in tags:
        name = (tag.get("name") or "").strip()
        if name:
            names.append(name)
    return names[:top_n]


def fetch_track_tags_lastfm(api_key: str, artist: str, track: str, top_n: int = 5) -> List[str]:
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.gettoptags",
        "artist": artist,
        "track": track,
        "api_key": api_key,
        "format": "json",
        "autocorrect": 1,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("error"):
        return []
    return _extract_top_tag_names(data, top_n=top_n)


def fetch_artist_tags_lastfm(api_key: str, artist: str, top_n: int = 5) -> List[str]:
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.gettoptags",
        "artist": artist,
        "api_key": api_key,
        "format": "json",
        "autocorrect": 1,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("error"):
        return []
    return _extract_top_tag_names(data, top_n=top_n)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    RAW_DIR.mkdir(exist_ok=True)

    load_dotenv()
    api_key = os.getenv("LASTFM_API_KEY", "").strip()
    username = os.getenv("LASTFM_USER", "").strip()

    to_ts = now_utc_ts()
    from_ts = to_ts - 7 * 24 * 3600

    source = "mock"

    if not (api_key and username):
        print("[WARN] Missing LASTFM_API_KEY or LASTFM_USER; fallback to demo.")
        data = demo_week_data(username=username or "demo_user")
    else:
        try:
            raw = fetch_recent_tracks_lastfm(
                api_key=api_key, username=username, from_ts=from_ts, to_ts=to_ts
            )
            (RAW_DIR / "lastfm_recenttracks.json").write_text(
                json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            scrobbles = normalize_scrobbles(raw)
            if not scrobbles:
                raise RuntimeError(
                    "Fetched 0 scrobbles (maybe no scrobbles in last 7 days)."
                )

            # === tags：去重 + 快取 ===
            cache = load_tags_cache()

            # 本週出現的「不同歌曲」
            unique_keys: Dict[str, Tuple[str, str]] = {}
            for s in scrobbles:
                k = safe_track_key(s["artist"], s["track"])
                unique_keys[k] = (s["artist"], s["track"])

            # ⭐ 抓 100 首不同歌的 tags（會比較慢）
            max_new_fetch = 100
            new_fetch_count = 0

            for k, (artist, track) in unique_keys.items():
                # cache 裡有「非空 tags」才跳過；
                # 若 cache 是 [] 或缺值，允許再試一次。
                if k in cache and cache.get(k):
                    continue

                if new_fetch_count >= max_new_fetch:
                    break

                tags = fetch_track_tags_lastfm(
                    api_key=api_key, artist=artist, track=track, top_n=5
                )
                if not tags:
                    tags = fetch_artist_tags_lastfm(
                        api_key=api_key, artist=artist, top_n=5
                    )
                if not tags:
                    tags = FALLBACK_TAGS  # ⭐ 最後保底，確保非空

                cache[k] = tags
                new_fetch_count += 1

                # 稍微放慢，避免太密集（新手安全值）
                time.sleep(0.2)

            save_tags_cache(cache)

            # 把 tags 塞回每筆 scrobble（永遠非空）
            for s in scrobbles:
                k = safe_track_key(s["artist"], s["track"])
                s["tags"] = cache.get(k) or FALLBACK_TAGS

            data = {
                "user": {"username": username},
                "range": {"from_ts": from_ts, "to_ts": to_ts},
                "scrobbles": scrobbles,
            }
            source = "lastfm"

        except Exception as e:
            print(f"[WARN] Last.fm fetch failed, fallback to demo. reason={e}")
            data = demo_week_data(username=username or "demo_user")

    out_path = OUT_DIR / "week_data.json"
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    scrobble_count = len(data.get("scrobbles", []))
    unique_song_count = len(
        {safe_track_key(s["artist"], s["track"]) for s in data.get("scrobbles", [])}
    )

    # 「真 tags」：排除 ["untagged"] 的計數（更能反映品質）
    nonempty_tag_count = sum(1 for s in data.get("scrobbles", []) if s.get("tags"))
    real_tag_count = sum(
        1 for s in data.get("scrobbles", [])
        if s.get("tags") and s.get("tags") != FALLBACK_TAGS
    )

    print(f"[OK] wrote {out_path} (source={source}, scrobble_count={scrobble_count})")
    if source == "lastfm":
        print(
            f"[INFO] tags_cache={TAGS_CACHE_PATH} (not uploaded), new_tags_fetched_up_to={max_new_fetch}"
        )
        print(
            f"[INFO] unique_songs={unique_song_count}, scrobbles_with_any_tags={nonempty_tag_count}, "
            f"scrobbles_with_real_tags={real_tag_count}, real_tag_coverage={real_tag_count/scrobble_count:.1%}"
        )
        print(
            "[INFO] Note: tags are guaranteed non-empty; ['untagged'] is a local fallback (not from Last.fm)."
        )


if __name__ == "__main__":
    main()
