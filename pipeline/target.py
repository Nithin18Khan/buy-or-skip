from __future__ import annotations

import json
import os
from pathlib import Path


def growth(root: Path) -> dict:
    return json.loads((root / "config" / "growth.json").read_text(encoding="utf-8"))


def load_revenue(root: Path) -> dict:
    path = root / "data" / "revenue.json"
    if not path.exists():
        return {"affiliate_usd": 0, "youtube_ads_usd": 0, "notes": ""}
    return json.loads(path.read_text(encoding="utf-8"))


def save_revenue(root: Path, data: dict) -> None:
    path = root / "data" / "revenue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def evaluate_target(root: Path, *, youtube_ads_usd: float | None = None) -> dict:
    g = growth(root)
    cap = float(g.get("stop_uploads_at_usd") or g.get("stretch_usd") or 1_000_000)
    stored = load_revenue(root)
    env_aff = os.environ.get("AFFILIATE_REVENUE_USD", "").strip()
    if env_aff:
        affiliate = float(env_aff)
        stored["affiliate_usd"] = affiliate
        save_revenue(root, stored)
    else:
        affiliate = float(stored.get("affiliate_usd") or 0)
    ads = youtube_ads_usd
    if ads is None:
        ads = float(stored.get("youtube_ads_usd") or 0)
    total = affiliate + float(ads or 0)
    stop = total >= cap
    return {
        "stop_uploads": stop,
        "target_usd": cap,
        "affiliate_usd": affiliate,
        "youtube_ads_usd": float(ads or 0),
        "total_usd": total,
        "remaining_usd": max(0.0, cap - total),
        "action": "STOP uploads — $1M reached" if stop else "KEEP uploading",
    }
