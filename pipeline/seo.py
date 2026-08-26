from __future__ import annotations

from pipeline.chapters import chapter_stamps

PROGRAM_HASH = {
    "hostinger": ["#Hostinger", "#WebHosting", "#WordPress"],
    "canva": ["#CanvaPro", "#Canva", "#GraphicDesign"],
    "nordvpn": ["#NordVPN", "#VPN", "#Privacy"],
    "amazon_in": ["#ToolsReview", "#BuyOrSkip", "#Review"],
}

PROGRAM_TAGS = {
    "hostinger": [
        "hostinger review",
        "hostinger vs cheap hosting",
        "hostinger renewal",
        "web hosting 2026",
        "wordpress hosting",
        "is hostinger worth it",
    ],
    "canva": [
        "canva pro review",
        "canva pro vs free",
        "is canva pro worth it",
        "canva pro 2026",
        "canva background remover",
        "canva brand kit",
    ],
    "nordvpn": [
        "nordvpn review",
        "nordvpn vs free vpn",
        "is nordvpn worth it",
        "vpn 2026",
    ],
    "amazon_in": ["tool review", "buy or skip", "software review"],
}


def _clean_tag(tag: str) -> str:
    tag = str(tag).strip()
    if not tag:
        return ""
    if not tag.startswith("#"):
        tag = "#" + tag.replace(" ", "")
    return tag


def hashtags(episode: dict) -> list[str]:
    raw = episode.get("hashtags") or []
    tags = [_clean_tag(x) for x in raw if _clean_tag(x)]
    pid = str((episode.get("affiliate") or {}).get("program") or "")
    for item in PROGRAM_HASH.get(pid, ["#ToolsReview"]):
        if item not in tags:
            tags.append(item)
    if "#BuyOrSkip" not in tags:
        tags.append("#BuyOrSkip")
    return tags[:8]


def search_tags(episode: dict) -> list[str]:
    pid = str((episode.get("affiliate") or {}).get("program") or "")
    extra = [str(x).strip() for x in (episode.get("tags") or []) if str(x).strip()]
    core = PROGRAM_TAGS.get(pid, [])
    title = str(episode.get("youtube_title") or episode.get("title") or "")
    built = list(dict.fromkeys(core + extra + ["Buy or Skip", "buy or skip", "review", "2026", title]))
    return [t for t in built if t][:25]


def apply_seo(episode: dict, *, audio_chapters: list[dict] | None = None) -> dict:
    episode["hashtags"] = hashtags(episode)
    episode["tags"] = search_tags(episode)
    title = str(episode.get("youtube_title") or episode.get("title") or "Buy or Skip")[:100]
    episode["youtube_title"] = title
    hashes = " ".join(episode["hashtags"][:3])
    rest = " ".join(episode["hashtags"][3:])
    stamps = chapter_stamps(audio_chapters or [])
    body = str(episode.get("seo_body") or "").strip()
    if not body:
        body = str(episode.get("description") or title)
        if "{chapters}" in body:
            body = body.replace("{chapters}", stamps or "See timeline.")
        elif stamps and "Chapters" not in body:
            body = body.rstrip() + "\n\nChapters\n" + stamps
    else:
        body = body.replace("{chapters}", stamps or "See timeline.")
    if "this video contains affiliate links" not in body.lower():
        body = (
            "This video contains affiliate links. I may earn a commission if you buy, "
            "at no extra cost to you.\n\n" + body
        )
    if hashes and hashes not in body:
        parts = body.split("\n", 1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else ""
        body = f"{head}\n\n{hashes}\n{tail}".strip()
    if rest and rest not in body:
        body = body.rstrip() + "\n\n" + rest
    episode["description"] = body[:4900]
    return episode


def write_pack(episode: dict, out_dir) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "youtube_title.txt").write_text(str(episode.get("youtube_title") or ""), encoding="utf-8")
    (out_dir / "hashtags.txt").write_text(" ".join(episode.get("hashtags") or []), encoding="utf-8")
    (out_dir / "description.txt").write_text(str(episode.get("description") or ""), encoding="utf-8")
    (out_dir / "tags.txt").write_text("\n".join(episode.get("tags") or []), encoding="utf-8")
