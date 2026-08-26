"""
Buy or Skip — adult affiliate YouTube factory.
Not Kids Edu Shorts. Not gaming. English. Never Made for Kids.
Uploads continue until combined revenue hits $1,000,000, then stop.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from pipeline.analytics import print_money_report, snapshot_analytics
from pipeline.assemble import assemble_long, assemble_trailer
from pipeline.calendar import write_90_day
from pipeline.detect import print_tool_report
from pipeline.links import apply_tracking_url, check_program_links, print_link_report
from pipeline.queue import load_manifest, load_state, pending, save_state
from pipeline.target import evaluate_target
from pipeline.seo import apply_seo, write_pack
from pipeline.thumbnail import make_thumbnail
from pipeline.upload import upload_video, youtube_auth_available
from pipeline.voice import generate_chapter_audio, generate_short_voice


def _load_episode(path: Path) -> dict:
    episode = json.loads(path.read_text(encoding="utf-8"))
    if episode.get("made_for_kids") is True:
        raise SystemExit("Refuse: Money Tools cannot be Made for Kids")
    episode["made_for_kids"] = False
    episode["language"] = "en"
    apply_tracking_url(ROOT, episode)
    return episode


def _money_gate() -> dict:
    try:
        return snapshot_analytics(ROOT)
    except Exception as exc:
        report = evaluate_target(ROOT)
        report["youtube_error"] = str(exc)
        report["youtube_views"] = 0
        return report


def run_episode(episode_path: Path, *, dry_run: bool, do_upload: bool) -> Path | None:
    if not episode_path.is_absolute():
        episode_path = ROOT / episode_path
    episode = _load_episode(episode_path)
    print("=== Buy or Skip (adult) ===")
    print(f"ID:     {episode['id']}")
    print(f"Title:  {episode['title']}")
    print(f"Offer:  {(episode.get('affiliate') or {}).get('program')}")
    if dry_run:
        print("Dry run OK.")
        return None

    report = _money_gate()
    print_money_report(report)
    if do_upload and report.get("stop_uploads"):
        print("STOP: combined revenue hit $1,000,000. Rendering only — no upload.")
        do_upload = False

    out_dir = ROOT / "output" / episode["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "episode.json").write_text(
        json.dumps(episode, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    chapters = generate_chapter_audio(episode, out_dir)
    print(f"Voice:  {len(chapters)} chapters, {sum(c['duration'] for c in chapters):.0f}s")
    video = assemble_long(episode, out_dir, chapters[0]["audio"], root=ROOT, chapter_audio=chapters)
    apply_seo(episode, audio_chapters=chapters)
    write_pack(episode, out_dir)
    (out_dir / "episode.json").write_text(
        json.dumps(episode, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Title:  {episode.get('youtube_title')}")
    print(f"Tags:   {' '.join(episode.get('hashtags') or [])}")
    print(f"Long:   {video}")
    trailer = assemble_trailer(episode, out_dir, generate_short_voice(episode, out_dir), root=ROOT)
    print(f"Short:  {trailer}")
    thumb = make_thumbnail(episode, out_dir)
    print(f"Thumb:  {thumb}")
    st = load_state(ROOT)
    st.setdefault("rendered", {})[episode["id"]] = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "video": str(video.relative_to(ROOT)).replace("\\", "/"),
    }
    save_state(ROOT, st)
    if do_upload:
        tracking = str((episode.get("affiliate") or {}).get("tracking_url") or "").strip()
        if not tracking:
            print(
                "No affiliate.tracking_url. Set config/affiliates.json tracking_urls "
                "or GitHub secrets AFFILIATE_HOSTINGER_URL / CANVA / NORDVPN. Skip upload."
            )
            return video
        if not youtube_auth_available(ROOT):
            print("No OAuth yet. See credentials/HOW_TO_AUTH.txt")
            return video
        info = upload_video(episode, video, root=ROOT)
        st = load_state(ROOT)
        st.setdefault("uploaded", {})[episode["id"]] = {
            "at": datetime.now().isoformat(timespec="seconds"),
            "youtube": info,
        }
        save_state(ROOT, st)
        print(f"YouTube: {info.get('url')}")
    return video


def main() -> int:
    parser = argparse.ArgumentParser(description="Buy or Skip adult affiliate factory")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plan-90", action="store_true", help="Write 24 unique long-form episode JSON files")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--check-links", action="store_true", help="Probe official affiliate join URLs")
    parser.add_argument("--episode", default=None)
    parser.add_argument("--next", action="store_true", help="Render the next unpublished long video")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()

    if args.check:
        return print_tool_report(ROOT)

    if args.check_links:
        report = check_program_links(ROOT)
        print_link_report(report)
        return 0 if report.get("ok") else 1

    if args.plan_90:
        path = write_90_day(ROOT)
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"Wrote {data['long_videos']} long-form scripts → {path}")
        print("Cadence: 2 unique videos per week for 90 days.")
        print("Paste real tracking URLs into config/affiliates.json tracking_urls.")
        return 0

    if args.status:
        g = json.loads((ROOT / "config" / "growth.json").read_text(encoding="utf-8"))
        print("=== Growth (honest) ===")
        print(g.get("honest"))
        report = _money_gate()
        print_money_report(report)
        links = check_program_links(ROOT)
        print_link_report(links)
        try:
            man = load_manifest(ROOT)
        except FileNotFoundError as exc:
            print(exc)
            return 1
        st = load_state(ROOT)
        print(f"Calendar:  {man['long_videos']} long videos")
        print(f"Rendered:  {len(st.get('rendered') or {})}")
        print(f"Uploaded:  {len(st.get('uploaded') or {})}")
        nxt = pending(ROOT, need="render")
        print(f"Next:      {nxt[0]['id'] if nxt else 'none'}")
        print(f"OAuth:     {'yes' if youtube_auth_available(ROOT) else 'no — credentials/HOW_TO_AUTH.txt'}")
        if not nxt and not report.get("stop_uploads"):
            print("Queue empty but $1M not reached. Add more unique episode JSON files.")
        return 0

    path = None
    if args.episode:
        path = Path(args.episode)
    elif args.next:
        report = _money_gate()
        print_money_report(report)
        if report.get("stop_uploads") and args.upload:
            print("STOP: $1,000,000 reached. No more uploads.")
            return 0
        nxt = pending(ROOT, need="render")
        if not nxt:
            if report.get("stop_uploads"):
                print("Queue empty and $1M reached. Factory done.")
                return 0
            print("Queue empty but $1M not reached. Add unique episode JSON, then --plan-90.")
            return 1
        path = ROOT / nxt[0]["file"]
    if path:
        run_episode(path, dry_run=args.dry_run, do_upload=args.upload)
        return 0

    parser.error("Pass --check, --plan-90, --status, --check-links, --episode, or --next")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
