from __future__ import annotations

from typing import Any


def _join(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(x).strip() for x in value if str(x).strip())
    return str(value or "").strip()


def chapter_text(chapter: dict) -> str:
    return _join(chapter.get("narration"))


def episode_chapters(episode: dict) -> list[dict]:
    raw = episode.get("chapters")
    if isinstance(raw, list) and raw:
        out: list[dict] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            cid = str(item.get("id") or f"c{len(out):02d}")
            out.append(
                {
                    "id": cid,
                    "label": str(item.get("label") or cid.replace("_", " ")).strip(),
                    "narration": chapter_text(item),
                    "record": str(item.get("record") or "").strip(),
                    "capture_url": str(item.get("capture_url") or "").strip(),
                }
            )
        return [c for c in out if c["narration"]]
    lines = episode.get("narration") or []
    text = _join(lines)
    if not text:
        return []
    return [
        {
            "id": "full",
            "label": str(episode.get("title") or "Review"),
            "narration": text,
            "record": "",
            "capture_url": "",
        }
    ]


def short_text(episode: dict) -> str:
    short = _join(episode.get("short_narration"))
    if short:
        return short
    chapters = episode_chapters(episode)
    if chapters:
        return chapters[0]["narration"]
    return _join(episode.get("narration"))


def chapter_stamps(audio_chapters: list[dict]) -> str:
    t = 0.0
    lines: list[str] = []
    for item in audio_chapters:
        if str(item.get("id") or "") == "disclosure":
            t += float(item.get("duration") or 0)
            continue
        mins = int(t // 60)
        secs = int(t % 60)
        label = str(item.get("label") or item.get("id") or "")
        lines.append(f"{mins}:{secs:02d} {label}")
        t += float(item.get("duration") or 0)
    return "\n".join(lines)


def apply_chapter_stamps(episode: dict, audio_chapters: list[dict]) -> str:
    desc = str(episode.get("description") or episode.get("title") or "")
    stamps = chapter_stamps(audio_chapters)
    if "{chapters}" in desc:
        desc = desc.replace("{chapters}", stamps or "See timeline.")
    elif stamps:
        desc = desc.rstrip() + "\n\nChapters\n" + stamps
    episode["description"] = desc
    return desc
