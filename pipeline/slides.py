from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pipeline.identity import BG, CHANNEL, GOLD, HANDLE, INK, MUTED, TAGLINE, fonts, program_color


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:8]


def render_slides(episode: dict, out_dir: Path) -> list[Path]:
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 64)
    label_f = ImageFont.truetype(str(bold), 28)
    body_f = ImageFont.truetype(str(regular), 36)
    small_f = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    shots = episode.get("shots") or [{"id": "hook", "label": "HOOK", "line": episode["title"]}]
    for i, shot in enumerate(shots):
        im = Image.new("RGB", (1920, 1080), BG)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 18, 1080), fill=accent)
        d.rectangle((0, 1048, 1920, 1080), fill=accent)
        d.text((64, 48), CHANNEL.upper(), font=label_f, fill=GOLD)
        d.text((420, 52), HANDLE, font=small_f, fill=MUTED)
        d.text((64, 96), TAGLINE, font=small_f, fill=MUTED)
        label = str(shot.get("label") or shot.get("id") or "").upper()
        d.text((64, 200), label, font=label_f, fill=accent)
        line = str(shot.get("line") or episode["title"])
        y = 280
        for wrapped in _wrap(d, line, body_f, 1760):
            d.text((64, y), wrapped, font=body_f, fill=INK)
            y += 52
        if i == 0:
            for wrapped in _wrap(d, str(episode["title"]), title_f, 1760)[:3]:
                d.text((64, 720), wrapped, font=title_f, fill=INK)
        d.text((64, 980), "18+  ·  Not for children  ·  One offer in the description", font=small_f, fill=MUTED)
        path = slides_dir / f"slide_{i:02d}.png"
        im.save(path, "PNG")
        paths.append(path)
    return paths


def render_vertical_slides(episode: dict, out_dir: Path) -> list[Path]:
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 56)
    label_f = ImageFont.truetype(str(bold), 26)
    body_f = ImageFont.truetype(str(regular), 32)
    accent = program_color(episode)
    slides_dir = out_dir / "slides_vertical"
    slides_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    shots = (episode.get("shots") or [])[:4] or [{"label": "HOOK", "line": episode["title"]}]
    for i, shot in enumerate(shots):
        im = Image.new("RGB", (1080, 1920), BG)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 1080, 16), fill=accent)
        d.rectangle((0, 1904, 1080, 1920), fill=accent)
        d.text((48, 80), CHANNEL.upper(), font=label_f, fill=GOLD)
        y = 220
        for wrapped in _wrap(d, str(episode["title"]), title_f, 980)[:5]:
            d.text((48, y), wrapped, font=title_f, fill=INK)
            y += 70
        d.text((48, y + 40), str(shot.get("label") or "").upper(), font=label_f, fill=accent)
        y2 = y + 100
        for wrapped in _wrap(d, str(shot.get("line") or ""), body_f, 980):
            d.text((48, y2), wrapped, font=body_f, fill=INK)
            y2 += 44
        d.text((48, 1780), "Full verdict on the channel", font=body_f, fill=GOLD)
        path = slides_dir / f"v_{i:02d}.png"
        im.save(path, "PNG")
        paths.append(path)
    return paths
