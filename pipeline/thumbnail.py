from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pipeline.identity import BG, CHANNEL, GOLD, INK, fonts, program_color
from pipeline.slides import _wrap


def make_thumbnail(episode: dict, out_dir: Path) -> Path:
    bold, regular = fonts()
    huge = ImageFont.truetype(str(bold), 72)
    mid = ImageFont.truetype(str(bold), 36)
    small = ImageFont.truetype(str(regular), 24)
    accent = program_color(episode)
    im = Image.new("RGB", (1280, 720), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 24, 720), fill=accent)
    d.rectangle((24, 0, 1280, 90), fill=(16, 18, 24))
    d.text((48, 28), CHANNEL.upper(), font=mid, fill=GOLD)
    d.rounded_rectangle((48, 140, 320, 210), radius=8, fill=accent)
    d.text((72, 155), "VERDICT", font=mid, fill=BG)
    y = 240
    for line in _wrap(d, str(episode["title"]), huge, 1160)[:4]:
        d.text((48, y), line, font=huge, fill=INK)
        y += 82
    d.text((48, 640), "Buy  ·  Wait  ·  Skip     18+", font=small, fill=GOLD)
    path = out_dir / "thumbnail.jpg"
    im.save(path, "JPEG", quality=92)
    return path
