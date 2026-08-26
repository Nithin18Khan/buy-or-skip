from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pipeline.identity import BG, CHANNEL, GOLD, INK, MUTED, fonts, program_color
from pipeline.slides import _card, _grid, _wrap


def make_thumbnail(episode: dict, out_dir: Path) -> Path:
    bold, regular = fonts()
    huge = ImageFont.truetype(str(bold), 58)
    hero = ImageFont.truetype(str(bold), 88)
    mid = ImageFont.truetype(str(bold), 30)
    small = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    facts = episode.get("facts") or {}
    im = Image.new("RGB", (1280, 720), BG)
    d = ImageDraw.Draw(im)
    _grid(d, 1280, 720)
    d.rectangle((0, 0, 18, 720), fill=accent)
    d.text((40, 24), CHANNEL.upper(), font=mid, fill=GOLD)
    stamp = str(facts.get("verdict") or "VERDICT").upper()
    stamp_color = GOLD if stamp == "BUY" else ((220, 90, 90) if stamp == "SKIP" else accent)
    _card(d, (40, 78, 260, 158), fill=stamp_color, outline=stamp_color)
    d.text((58, 96), stamp[:8], font=mid, fill=BG)
    hook = str(facts.get("thumb_title") or episode.get("title") or episode.get("youtube_title") or "")
    y = 186
    for line in _wrap(d, hook, huge, 1180)[:2]:
        d.text((40, y), line, font=huge, fill=INK)
        y += 68
    left = str(facts.get("promo") or facts.get("left") or "")
    right = str(facts.get("renewal") or facts.get("right") or "")
    left_note = str(facts.get("left_note") or facts.get("term") or "")
    right_note = str(facts.get("right_note") or "")
    if left and right:
        _card(d, (40, 430, 610, 650), fill=(16, 18, 24), outline=accent)
        _card(d, (650, 430, 1240, 650), fill=(16, 18, 24), outline=(90, 50, 50))
        d.text((64, 460), left, font=hero, fill=INK)
        d.text((674, 460), right, font=hero, fill=INK)
        if left_note:
            d.text((64, 590), left_note[:28], font=small, fill=MUTED)
        if right_note:
            d.text((674, 590), right_note[:28], font=small, fill=(220, 90, 90))
    hashes = " ".join((episode.get("hashtags") or [])[:3])
    if hashes:
        d.text((40, 672), hashes, font=small, fill=GOLD)
    path = out_dir / "thumbnail.jpg"
    im.save(path, "JPEG", quality=92)
    return path
