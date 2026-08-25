"""
Money Tools — adult affiliate YouTube factory.
Not Kids Edu Shorts. Not gaming. English. Never Made for Kids.
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

from pipeline.assemble import assemble_long, assemble_trailer
from pipeline.calendar import write_90_day
from pipeline.detect import print_tool_report
from pipeline.queue import load_manifest, load_state, pending, save_state
from pipeline.thumbnail import make_thumbnail
from pipeline.upload import upload_video, youtube_auth_available
from pipeline.voice import generate_voiceover


def _load_episode(path: Path) -> dict:
    episode = json.loads(path.read_text(encoding="utf-8"))
    if episode.get("made_for_kids") is True:
        raise SystemExit("Refuse: Money Tools cannot be Made for Kids")
    episode["made_for_kids"] = False
    episode["language"] = "en"
    return episode


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
    out_dir = ROOT / "output" / episode["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "episode.json").write_text(
        json.dumps(episode, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    voice = generate_voiceover(episode, out_dir)
    print(f"Voice:  {voice}")
    video = assemble_long(episode, out_dir, voice, root=ROOT)
    print(f"Long:   {video}")
    trailer = assemble_trailer(episode, out_dir, voice, root=ROOT)
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
    parser = argparse.ArgumentParser(description="Money Tools adult affiliate factory")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plan-90", action="store_true", help="Write 24 unique long-form episode JSON files")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--episode", default=None)
    parser.add_argument("--next", action="store_true", help="Render the next unpublished long video")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()

    if args.check:
        return print_tool_report(ROOT)

    if args.plan_90:
        path = write_90_day(ROOT)
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"Wrote {data['long_videos']} long-form scripts → {path}")
        print("Cadence: 2 unique videos per week for 90 days.")
        print("Paste real affiliate.tracking_url into each JSON before upload.")
        return 0

    if args.status:
        g = json.loads((ROOT / "config" / "growth.json").read_text(encoding="utf-8"))
        print("=== Growth (honest) ===")
        print(g.get("honest"))
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
        return 0

    path = None
    if args.episode:
        path = Path(args.episode)
    elif args.next:
        nxt = pending(ROOT, need="render")
        if not nxt:
            print("90-day queue is complete.")
            return 0
        path = ROOT / nxt[0]["file"]
    if path:
        run_episode(path, dry_run=args.dry_run, do_upload=args.upload)
        return 0

    parser.error("Pass --check, --plan-90, --status, --episode, or --next")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
