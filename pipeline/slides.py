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


def _grid(d: ImageDraw.ImageDraw, w: int, h: int) -> None:
    for x in range(0, w, 80):
        d.line((x, 0, x, h), fill=(18, 21, 28))
    for y in range(0, h, 80):
        d.line((0, y, w, y), fill=(18, 21, 28))


def _chrome(d: ImageDraw.ImageDraw, *, w: int, h: int, accent, label_f, small_f, bar: int = 18) -> None:
    d.rectangle((0, 0, bar, h), fill=accent)
    d.rectangle((0, h - 32, w, h), fill=accent)
    d.text((48, 36), CHANNEL.upper(), font=label_f, fill=GOLD)
    d.text((48 + d.textlength(CHANNEL.upper() + "   ", font=label_f), 42), HANDLE, font=small_f, fill=MUTED)
    d.text((48, 78), TAGLINE, font=small_f, fill=MUTED)
    d.text((48, h - 78), "18+  ·  Not for children  ·  Affiliate disclosure in the video", font=small_f, fill=MUTED)


def _card(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, fill, outline) -> None:
    d.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=2)


def render_slides(episode: dict, out_dir: Path) -> list[Path]:
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 72)
    hero_f = ImageFont.truetype(str(bold), 120)
    label_f = ImageFont.truetype(str(bold), 26)
    body_f = ImageFont.truetype(str(regular), 38)
    small_f = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    facts = episode.get("facts") or {}
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    shots = episode.get("shots") or [{"id": "hook", "label": "HOOK", "line": episode["title"]}]
    panel = (16, 18, 24)
    for i, shot in enumerate(shots):
        im = Image.new("RGB", (1920, 1080), BG)
        d = ImageDraw.Draw(im)
        _grid(d, 1920, 1080)
        _chrome(d, w=1920, h=1080, accent=accent, label_f=label_f, small_f=small_f)
        kind = str(shot.get("id") or shot.get("kind") or "")
        label = str(shot.get("label") or kind).upper()
        line = str(shot.get("line") or episode["title"])
        d.text((48, 140), label, font=label_f, fill=accent)

        if kind == "hook":
            y = 210
            for wrapped in _wrap(d, str(episode["title"]), title_f, 1820)[:3]:
                d.text((48, y), wrapped, font=title_f, fill=INK)
                y += 86
            d.text((48, y + 12), line, font=body_f, fill=MUTED)
            promo = str(facts.get("promo") or "")
            renew = str(facts.get("renewal") or "")
            if promo and renew:
                _card(d, (48, 720, 900, 960), fill=panel, outline=accent)
                _card(d, (960, 720, 1810, 960), fill=panel, outline=(80, 40, 40))
                d.text((80, 750), "HOMEPAGE TEASE", font=label_f, fill=accent)
                d.text((80, 800), promo, font=hero_f, fill=INK)
                d.text((992, 750), "AFTER THE TERM", font=label_f, fill=(220, 90, 90))
                d.text((992, 800), renew, font=hero_f, fill=INK)

        elif kind == "price":
            promo = str(facts.get("promo") or "$2.99/mo")
            renew = str(facts.get("renewal") or "$10.99/mo")
            prepaid = str(facts.get("prepaid") or "")
            term = str(facts.get("term") or "")
            _card(d, (48, 220, 900, 700), fill=panel, outline=accent)
            _card(d, (960, 220, 1810, 700), fill=panel, outline=(90, 50, 50))
            d.text((80, 260), "LOCK-IN PRICE", font=label_f, fill=accent)
            d.text((80, 330), promo, font=hero_f, fill=INK)
            d.text((80, 500), term, font=body_f, fill=MUTED)
            d.text((80, 560), prepaid, font=body_f, fill=GOLD)
            d.text((992, 260), "RENEWAL BILL", font=label_f, fill=(220, 90, 90))
            d.text((992, 330), renew, font=hero_f, fill=INK)
            d.text((992, 520), "This is the real monthly cost", font=body_f, fill=MUTED)
            y = 760
            for wrapped in _wrap(d, line, body_f, 1760)[:4]:
                d.text((48, y), wrapped, font=body_f, fill=INK)
                y += 48

        elif kind == "verdict":
            stamp = str(facts.get("verdict") or "BUY").upper()
            color = GOLD if stamp == "BUY" else ((220, 90, 90) if stamp == "SKIP" else accent)
            _card(d, (48, 220, 520, 480), fill=color, outline=color)
            d.text((90, 300), stamp, font=hero_f, fill=BG)
            y = 240
            for wrapped in _wrap(d, line, body_f, 1200)[:8]:
                d.text((560, y), wrapped, font=body_f, fill=INK)
                y += 50
            d.text((48, 760), "Who should skip is in the same sentence. That is the review.", font=body_f, fill=MUTED)

        elif kind == "end":
            d.text((48, 280), "ONE LINK. ONE OFFER.", font=title_f, fill=INK)
            y = 420
            for wrapped in _wrap(d, line, body_f, 1760):
                d.text((48, y), wrapped, font=body_f, fill=MUTED)
                y += 50
            d.text((48, 720), "Full verdict on Buy or Skip", font=title_f, fill=GOLD)

        else:
            y = 240
            for wrapped in _wrap(d, line, body_f, 1760):
                d.text((48, y), wrapped, font=body_f, fill=INK)
                y += 54

        path = slides_dir / f"slide_{i:02d}.png"
        im.save(path, "PNG")
        paths.append(path)
    return paths


def render_vertical_slides(episode: dict, out_dir: Path) -> list[Path]:
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 56)
    hero_f = ImageFont.truetype(str(bold), 88)
    label_f = ImageFont.truetype(str(bold), 24)
    body_f = ImageFont.truetype(str(regular), 34)
    small_f = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    facts = episode.get("facts") or {}
    slides_dir = out_dir / "slides_vertical"
    slides_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    shots = (episode.get("shots") or [])[:4] or [{"id": "hook", "label": "HOOK", "line": episode["title"]}]
    for i, shot in enumerate(shots):
        im = Image.new("RGB", (1080, 1920), BG)
        d = ImageDraw.Draw(im)
        _grid(d, 1080, 1920)
        d.rectangle((0, 0, 1080, 14), fill=accent)
        d.rectangle((0, 1906, 1080, 1920), fill=accent)
        d.text((48, 64), CHANNEL.upper(), font=label_f, fill=GOLD)
        d.text((48, 104), "18+ adult review", font=small_f, fill=MUTED)
        y = 180
        for wrapped in _wrap(d, str(episode["title"]), title_f, 980)[:5]:
            d.text((48, y), wrapped, font=title_f, fill=INK)
            y += 68
        d.text((48, y + 24), str(shot.get("label") or "").upper(), font=label_f, fill=accent)
        y2 = y + 80
        for wrapped in _wrap(d, str(shot.get("line") or ""), body_f, 980)[:7]:
            d.text((48, y2), wrapped, font=body_f, fill=INK)
            y2 += 44
        promo = str(facts.get("promo") or "")
        renew = str(facts.get("renewal") or "")
        if i == 0 and promo and renew:
            _card(d, (48, 1280, 500, 1600), fill=(16, 18, 24), outline=accent)
            _card(d, (540, 1280, 1032, 1600), fill=(16, 18, 24), outline=(90, 50, 50))
            d.text((72, 1320), promo, font=hero_f, fill=INK)
            d.text((564, 1320), renew, font=hero_f, fill=INK)
            d.text((72, 1480), "tease", font=small_f, fill=MUTED)
            d.text((564, 1480), "renewal", font=small_f, fill=(220, 90, 90))
        stamp = str(facts.get("verdict") or "")
        if stamp:
            d.text((48, 1680), stamp.upper(), font=hero_f, fill=GOLD)
        hashes = " ".join((episode.get("hashtags") or [])[:3])
        d.text((48, 1800), hashes or "Full verdict on the channel", font=body_f, fill=GOLD)
        path = slides_dir / f"v_{i:02d}.png"
        im.save(path, "PNG")
        paths.append(path)
    return paths


def render_chapter_card(episode: dict, chapter: dict, dest: Path) -> Path:
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 64)
    hero_f = ImageFont.truetype(str(bold), 110)
    label_f = ImageFont.truetype(str(bold), 26)
    body_f = ImageFont.truetype(str(regular), 36)
    small_f = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    facts = episode.get("facts") or {}
    kind = str(chapter.get("id") or "")
    label = str(chapter.get("label") or kind).upper()
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    _grid(d, 1920, 1080)
    _chrome(d, w=1920, h=1080, accent=accent, label_f=label_f, small_f=small_f)
    d.text((48, 140), label, font=label_f, fill=accent)
    panel = (16, 18, 24)
    promo = str(facts.get("promo") or "")
    renew = str(facts.get("renewal") or "")
    prepaid = str(facts.get("prepaid") or "")
    term = str(facts.get("term") or "")

    if kind in {"hook", "price"}:
        _card(d, (48, 240, 900, 720), fill=panel, outline=accent)
        _card(d, (960, 240, 1872, 720), fill=panel, outline=(90, 50, 50))
        d.text((80, 280), "HOMEPAGE TEASE", font=label_f, fill=accent)
        d.text((80, 360), promo or "$2.99/mo", font=hero_f, fill=INK)
        d.text((80, 560), term or "48-month lock", font=body_f, fill=MUTED)
        d.text((80, 620), prepaid, font=body_f, fill=GOLD)
        d.text((992, 280), "AFTER THE TERM", font=label_f, fill=(220, 90, 90))
        d.text((992, 360), renew or "$10.99/mo", font=hero_f, fill=INK)
        d.text((992, 560), "This is the real monthly cost", font=body_f, fill=MUTED)
    elif kind == "who":
        _card(d, (48, 240, 900, 860), fill=panel, outline=accent)
        _card(d, (960, 240, 1872, 860), fill=panel, outline=(90, 50, 50))
        d.text((80, 280), "BUY IF", font=label_f, fill=accent)
        y = 360
        for line in (
            "Real site this month",
            "Shop, portfolio, WordPress you keep",
            "Month-13 math already done",
        ):
            d.text((80, y), line, font=body_f, fill=INK)
            y += 70
        d.text((992, 280), "SKIP IF", font=label_f, fill=(220, 90, 90))
        y = 360
        for line in (
            "Site is still a maybe",
            "Need daily backups day one",
            "Refuse a four-year prepay",
        ):
            d.text((992, y), line, font=body_f, fill=INK)
            y += 70
    elif kind == "panel":
        d.text((48, 240), "WHAT PREMIUM ACTUALLY INCLUDES", font=title_f, fill=INK)
        items = (
            ("hPanel", "Built for first-time WordPress"),
            ("3 sites", "Not unlimited. Fourth site is another plan."),
            ("SSL", "In the flow. Do not buy a separate cert."),
            ("Weekly backup", "Not daily. Shops should treat that as a limit."),
        )
        y = 360
        for title, note in items:
            _card(d, (48, y, 1872, y + 130), fill=panel, outline=accent)
            d.text((80, y + 20), title, font=label_f, fill=GOLD)
            d.text((80, y + 64), note, font=body_f, fill=INK)
            y += 150
    elif kind == "speed":
        _card(d, (48, 260, 900, 780), fill=panel, outline=accent)
        _card(d, (960, 260, 1872, 780), fill=panel, outline=(90, 50, 50))
        d.text((80, 300), "THIS PRICE", font=label_f, fill=accent)
        d.text((80, 400), "LiteSpeed", font=hero_f, fill=INK)
        d.text((80, 560), "Real stack if the theme is clean", font=body_f, fill=MUTED)
        d.text((992, 300), "NO-NAME HOST", font=label_f, fill=(220, 90, 90))
        d.text((992, 400), "Noisy disk", font=hero_f, fill=INK)
        d.text((992, 560), "Matches the teaser. Dies on traffic.", font=body_f, fill=MUTED)
    elif kind == "catch":
        d.text((48, 240), "THE CATCH", font=title_f, fill=INK)
        rows = (
            ("Backups", "Weekly, not daily"),
            ("Sites", "Three. Then you upgrade."),
            ("Support", "Chat. Not an enterprise SLA."),
            ("Term", "Four years prepaid for the teaser"),
        )
        x = 48
        for title, note in rows:
            _card(d, (x, 380, x + 430, 820), fill=panel, outline=accent)
            d.text((x + 28, 430), title.upper(), font=label_f, fill=GOLD)
            y_note = 520
            for wrapped in _wrap(d, note, body_f, 370)[:4]:
                d.text((x + 28, y_note), wrapped, font=body_f, fill=INK)
                y_note += 44
            x += 462
    elif kind == "verdict":
        stamp = str(facts.get("verdict") or "BUY").upper()
        color = GOLD if stamp == "BUY" else ((220, 90, 90) if stamp == "SKIP" else accent)
        _card(d, (48, 280, 520, 560), fill=color, outline=color)
        d.text((90, 350), stamp, font=hero_f, fill=BG)
        y = 300
        for line in (
            "Buy Premium if the site is real and month-13 still works.",
            "Skip if you need daily backups, more than 3 sites, or no 4-year prepay.",
            "Wait if the site is still a maybe.",
        ):
            for wrapped in _wrap(d, line, body_f, 1240)[:3]:
                d.text((560, y), wrapped, font=body_f, fill=INK)
                y += 48
            y += 18
    elif kind == "cta":
        d.text((48, 280), "ONE LINK. LIVE PRICE.", font=title_f, fill=INK)
        d.text((48, 420), "Hostinger is the first link in the description.", font=body_f, fill=INK)
        d.text((48, 490), "Read today's teaser, today's total, and today's renewal.", font=body_f, fill=INK)
        d.text((48, 620), "If month thirteen does not work, do not buy.", font=body_f, fill=GOLD)
    elif kind == "disclosure":
        d.text((48, 320), "LINKS IN THE DESCRIPTION ARE AFFILIATE.", font=title_f, fill=INK)
        d.text((48, 460), "You pay the same price either way.", font=body_f, fill=INK)
        d.text((48, 530), "Recheck the live page before you pay.", font=body_f, fill=MUTED)
    else:
        y = 280
        for wrapped in _wrap(d, label.title(), title_f, 1760)[:4]:
            d.text((48, y), wrapped, font=title_f, fill=INK)
            y += 80

    im.save(dest, "PNG")
    return dest


def _split_beats(text: str) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    for word in str(text or "").split():
        buf.append(word)
        if word[-1:] in ".?!":
            line = " ".join(buf).strip()
            if line:
                chunks.append(line)
            buf = []
    if buf:
        chunks.append(" ".join(buf).strip())
    return chunks or [str(text or "Buy or Skip")]


def _beat_kind(line: str, chapter_id: str) -> str:
    t = line.lower()
    if any(k in t for k in ("two dollars ninety-nine", "two ninety-nine", "2.99", "teaser", "homepage")):
        return "promo"
    if any(k in t for k in ("ten dollars ninety-nine", "ten ninety-nine", "10.99", "renew")):
        return "renew"
    if any(k in t for k in ("one hundred forty-four", "prepaid", "forty-eight", "leaves your account")):
        return "prepaid"
    if "skip" in t and "buy" in t:
        return "split"
    if t.startswith("skip") or "skip premium" in t or "skip the" in t:
        return "skip"
    if t.startswith("buy") or "buy hostinger" in t or "buy means" in t:
        return "buy"
    if "wait" in t:
        return "wait"
    if any(k in t for k in ("backup", "weekly", "daily")):
        return "backup"
    if any(k in t for k in ("three site", "three slot", "fourth")):
        return "sites"
    if any(k in t for k in ("litespeed", "speed", "stutter", "first paint")):
        return "speed"
    if any(k in t for k in ("wordpress", "hpanel", "panel", "ssl", "brand kit", "background remover", "magic studio")):
        return "panel"
    if any(k in t for k in ("affiliate", "same price", "links in the description")):
        return "note"
    if chapter_id == "verdict" and t.startswith("verdict"):
        return "buy"
    return "quote"


def render_auto_beats(episode: dict, chapter: dict, dest_dir: Path, brand: Path | None = None) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    bold, regular = fonts()
    title_f = ImageFont.truetype(str(bold), 56)
    hero_f = ImageFont.truetype(str(bold), 120)
    label_f = ImageFont.truetype(str(bold), 26)
    body_f = ImageFont.truetype(str(regular), 38)
    small_f = ImageFont.truetype(str(regular), 22)
    accent = program_color(episode)
    facts = episode.get("facts") or {}
    promo = str(facts.get("promo") or "$2.99/mo")
    renew = str(facts.get("renewal") or "$10.99/mo")
    prepaid = str(facts.get("prepaid") or "~$144")
    label = str(chapter.get("label") or chapter.get("id") or "").upper()
    cid = str(chapter.get("id") or "beat")
    brand_im = None
    if brand and brand.exists():
        try:
            brand_im = Image.open(brand).convert("RGB").resize((1920, 1080))
        except OSError:
            brand_im = None
    paths: list[Path] = []
    beats = _split_beats(str(chapter.get("narration") or episode.get("title") or ""))
    for i, line in enumerate(beats):
        if brand_im is not None and i % 3 == 1:
            im = brand_im.copy()
            overlay = Image.new("RGB", (1920, 1080), BG)
            im = Image.blend(im, overlay, 0.72)
        else:
            im = Image.new("RGB", (1920, 1080), BG)
        d = ImageDraw.Draw(im)
        if brand_im is None or i % 3 != 1:
            _grid(d, 1920, 1080)
        _chrome(d, w=1920, h=1080, accent=accent, label_f=label_f, small_f=small_f)
        d.text((48, 140), label, font=label_f, fill=accent)
        kind = _beat_kind(line, cid)
        panel = (16, 18, 24)
        if kind == "promo":
            _card(d, (48, 240, 1872, 620), fill=panel, outline=accent)
            d.text((80, 280), "HOMEPAGE TEASE", font=label_f, fill=accent)
            d.text((80, 360), promo, font=hero_f, fill=INK)
        elif kind == "renew":
            _card(d, (48, 240, 1872, 620), fill=panel, outline=(90, 50, 50))
            d.text((80, 280), "AFTER THE TERM", font=label_f, fill=(220, 90, 90))
            d.text((80, 360), renew, font=hero_f, fill=INK)
        elif kind == "prepaid":
            _card(d, (48, 240, 1872, 620), fill=panel, outline=GOLD)
            d.text((80, 280), "DUE TODAY", font=label_f, fill=GOLD)
            d.text((80, 360), prepaid, font=hero_f, fill=INK)
        elif kind == "buy":
            _card(d, (48, 260, 620, 560), fill=GOLD, outline=GOLD)
            d.text((90, 340), "BUY", font=hero_f, fill=BG)
        elif kind == "skip":
            _card(d, (48, 260, 620, 560), fill=(220, 90, 90), outline=(220, 90, 90))
            d.text((90, 340), "SKIP", font=hero_f, fill=BG)
        elif kind == "wait":
            _card(d, (48, 260, 620, 560), fill=accent, outline=accent)
            d.text((90, 340), "WAIT", font=hero_f, fill=BG)
        elif kind == "split":
            _card(d, (48, 240, 900, 560), fill=GOLD, outline=GOLD)
            _card(d, (960, 240, 1872, 560), fill=(220, 90, 90), outline=(220, 90, 90))
            d.text((90, 340), "BUY", font=hero_f, fill=BG)
            d.text((1000, 340), "SKIP", font=hero_f, fill=BG)
        elif kind == "backup":
            _card(d, (48, 240, 1872, 560), fill=panel, outline=(220, 90, 90))
            d.text((80, 280), "THE CATCH", font=label_f, fill=(220, 90, 90))
            d.text((80, 360), "Weekly backups", font=title_f, fill=INK)
        elif kind == "sites":
            _card(d, (48, 240, 1872, 560), fill=panel, outline=accent)
            d.text((80, 280), "PREMIUM LIMIT", font=label_f, fill=accent)
            d.text((80, 360), "3 sites", font=hero_f, fill=INK)
        elif kind == "speed":
            _card(d, (48, 240, 1872, 560), fill=panel, outline=accent)
            d.text((80, 280), "STACK", font=label_f, fill=accent)
            d.text((80, 360), "LiteSpeed", font=hero_f, fill=INK)
        elif kind == "panel":
            _card(d, (48, 240, 1872, 560), fill=panel, outline=accent)
            d.text((80, 280), "WHAT YOU GET", font=label_f, fill=accent)
            d.text((80, 360), "hPanel + WordPress", font=title_f, fill=INK)
        elif kind == "note":
            _card(d, (48, 240, 1872, 560), fill=panel, outline=MUTED)
            d.text((80, 320), "Same price either way.", font=title_f, fill=INK)
        else:
            y = 280
            for wrapped in _wrap(d, line, title_f, 1760)[:5]:
                d.text((48, y), wrapped, font=title_f, fill=INK)
                y += 72
        cap_y = 720
        for wrapped in _wrap(d, line, body_f, 1760)[:4]:
            d.text((48, cap_y), wrapped, font=body_f, fill=MUTED)
            cap_y += 48
        path = dest_dir / f"{cid}_{i:02d}.png"
        im.save(path, "PNG")
        paths.append(path)
    return paths
