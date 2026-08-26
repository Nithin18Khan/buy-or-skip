"""Check official affiliate join URLs still resolve. Tracking IDs stay yours."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ENV_TRACKING = {
    "hostinger": "AFFILIATE_HOSTINGER_URL",
    "canva": "AFFILIATE_CANVA_URL",
    "nordvpn": "AFFILIATE_NORDVPN_URL",
    "amazon_in": "AFFILIATE_AMAZON_IN_URL",
}


def load_affiliates(root: Path) -> dict:
    return json.loads((root / "config" / "affiliates.json").read_text(encoding="utf-8"))


def resolve_tracking_url(root: Path, episode: dict) -> str:
    aff = episode.get("affiliate") or {}
    url = str(aff.get("tracking_url") or "").strip()
    if url:
        return url
    pid = str(aff.get("program") or "").strip()
    env_name = ENV_TRACKING.get(pid, "")
    if env_name:
        env_url = os.environ.get(env_name, "").strip()
        if env_url:
            return env_url
    blob = load_affiliates(root)
    return str((blob.get("tracking_urls") or {}).get(pid) or "").strip()


def apply_tracking_url(root: Path, episode: dict) -> str:
    url = resolve_tracking_url(root, episode)
    episode.setdefault("affiliate", {})["tracking_url"] = url
    return url


def episode_tracking_ok(root: Path, episode: dict) -> bool:
    return bool(resolve_tracking_url(root, episode))


def _probe(url: str, timeout: int = 12) -> dict:
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "BuyOrSkipLinkCheck/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = int(getattr(resp, "status", None) or resp.getcode())
            # 403 is common behind Cloudflare; page still exists.
            return {"url": url, "ok": 200 <= code < 400 or code == 403, "status": code}
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "ok": 200 <= exc.code < 400 or exc.code == 403,
            "status": exc.code,
        }
    except Exception as exc:
        return {"url": url, "ok": False, "status": 0, "error": str(exc)}


def program_urls(root: Path) -> list[str]:
    blob = load_affiliates(root)
    urls: list[str] = []
    for row in (blob.get("primary_programs") or []) + (blob.get("side_bucket") or []):
        for key in ("join_url", "signup_url", "dashboard_url"):
            u = str(row.get(key) or "").strip()
            if u:
                urls.append(u)
    return list(dict.fromkeys(urls))


def check_program_links(root: Path) -> dict:
    results = [_probe(u) for u in program_urls(root)]
    bad = [r for r in results if not r.get("ok")]
    return {"ok": not bad, "checked": results, "failed": bad}


def print_link_report(report: dict) -> None:
    print("=== Affiliate program URLs (official join pages) ===")
    for row in report.get("checked") or []:
        mark = "OK" if row.get("ok") else "DEAD"
        extra = f" {row.get('error')}" if row.get("error") else ""
        print(f"  [{mark}] {row.get('status')}  {row.get('url')}{extra}")
    if report.get("ok"):
        print("All official join URLs still resolve.")
    else:
        print("Some official URLs failed. Update config/affiliates.json.")
