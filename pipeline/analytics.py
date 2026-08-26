"""YouTube Analytics for Buy or Skip. Affiliate dashboards are not in this API."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from pipeline.target import evaluate_target, load_revenue, save_revenue
from pipeline.upload import get_youtube_creds, youtube_auth_available


def fetch_youtube_ads_usd(root: Path) -> dict:
    out: dict = {"ok": False, "youtube_ads_usd": 0.0, "views": 0, "error": ""}
    if not youtube_auth_available(root):
        out["error"] = "no YouTube OAuth yet"
        return out
    try:
        from googleapiclient.discovery import build

        creds = get_youtube_creds(root)
        analytics = build("youtubeAnalytics", "v2", credentials=creds)
        end = date.today().isoformat()
        try:
            resp = (
                analytics.reports()
                .query(
                    ids="channel==MINE",
                    startDate="2006-01-01",
                    endDate=end,
                    metrics="views,estimatedRevenue",
                )
                .execute()
            )
            rows = resp.get("rows") or [[0, 0]]
            out["views"] = float(rows[0][0] or 0)
            out["youtube_ads_usd"] = float(rows[0][1] or 0) if len(rows[0]) > 1 else 0.0
            out["ok"] = True
            out["error"] = ""
        except Exception as exc:
            resp = (
                analytics.reports()
                .query(
                    ids="channel==MINE",
                    startDate="2006-01-01",
                    endDate=end,
                    metrics="views",
                )
                .execute()
            )
            rows = resp.get("rows") or [[0]]
            out["views"] = float(rows[0][0] or 0)
            out["error"] = f"ads metric unavailable (need YPP + yt-analytics.readonly): {exc}"
    except Exception as exc:
        out["error"] = str(exc)
    return out


def snapshot_analytics(root: Path) -> dict:
    yt = fetch_youtube_ads_usd(root)
    stored = load_revenue(root)
    if yt.get("ok"):
        stored["youtube_ads_usd"] = yt["youtube_ads_usd"]
    stored["youtube_views"] = yt.get("views") or 0
    stored["checked_at"] = datetime.now(timezone.utc).isoformat()
    stored["youtube_error"] = yt.get("error") or ""
    save_revenue(root, stored)
    report = evaluate_target(root, youtube_ads_usd=stored.get("youtube_ads_usd"))
    report["youtube_views"] = stored.get("youtube_views") or 0
    report["youtube_error"] = stored.get("youtube_error") or ""
    report["checked_at"] = stored["checked_at"]
    return report


def print_money_report(report: dict) -> None:
    print("=== $1M upload gate (Buy or Skip only) ===")
    print(f"Target:     ${report['target_usd']:,.0f}")
    print(f"Affiliate:  ${report['affiliate_usd']:,.2f}  (dashboards / AFFILIATE_REVENUE_USD)")
    print(f"YT ads:     ${report['youtube_ads_usd']:,.2f}")
    print(f"Total:      ${report['total_usd']:,.2f}")
    print(f"Remaining:  ${report['remaining_usd']:,.2f}")
    print(f"Views:      {int(report.get('youtube_views') or 0):,}")
    print(f"Action:     {report['action']}")
    err = str(report.get("youtube_error") or "")
    if err:
        print(f"Analytics:  {err}")
