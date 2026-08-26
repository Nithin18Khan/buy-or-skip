from __future__ import annotations

import subprocess
import urllib.request
from pathlib import Path

VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


def footage_dir(root: Path, episode: dict) -> Path:
    return root / "footage" / str(episode["id"])


def _existing(paths: list[Path]) -> list[Path]:
    return [p for p in paths if p.is_file()]


def chapter_media(root: Path, episode: dict, chapter: dict) -> dict:
    folder = footage_dir(root, episode)
    cid = str(chapter.get("id") or "")
    videos = _existing([folder / f"{cid}{ext}" for ext in VIDEO_EXT])
    stills = _existing([folder / f"{cid}{ext}" for ext in IMAGE_EXT])
    extra = folder / cid
    if extra.is_dir():
        videos.extend(sorted(p for p in extra.iterdir() if p.suffix.lower() in VIDEO_EXT))
        stills.extend(sorted(p for p in extra.iterdir() if p.suffix.lower() in IMAGE_EXT))
    for idx in range(1, 8):
        stills.extend(_existing([folder / f"{cid}_{idx:02d}{ext}" for ext in IMAGE_EXT]))
    videos = list(dict.fromkeys(videos))
    stills = list(dict.fromkeys(stills))
    return {"videos": videos, "stills": stills, "dir": folder}


def find_chrome() -> Path | None:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def capture_public_page(url: str, dest: Path, *, chrome: Path) -> Path | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shot_name = dest.name if dest.suffix.lower() == ".png" else "screenshot.png"
    shot = dest.parent / shot_name
    if shot.exists():
        shot.unlink()
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-extensions",
        "--window-size=1920,1080",
        "--virtual-time-budget=10000",
        f"--screenshot={shot_name}",
        url,
    ]
    try:
        subprocess.run(cmd, check=True, cwd=str(dest.parent), timeout=50)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    if not shot.exists():
        fallback = dest.parent / "screenshot.png"
        if fallback.exists():
            shot = fallback
        else:
            return None
    if dest.resolve() != shot.resolve():
        if dest.exists():
            dest.unlink()
        shot.replace(dest)
    return dest if dest.exists() else None


BRAND_ASSETS = {
    "hostinger": (
        "https://www.hostinger.com/og-image.png",
        "https://www.hostinger.com/logo-400x400.png",
    ),
    "canva": (
        "https://www.canva.com/apple-touch-icon.png",
        "https://static.canva.com/static/images/canva-logo.png",
    ),
    "nordvpn": (
        "https://nordvpn.com/wp-content/uploads/2020/01/nordvpn-og.png",
    ),
}


def download_brand_stills(root: Path, episode: dict) -> list[Path]:
    pid = str((episode.get("affiliate") or {}).get("program") or "")
    urls = BRAND_ASSETS.get(pid) or ()
    folder = footage_dir(root, episode) / "auto"
    folder.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for i, url in enumerate(urls, start=1):
        dest = folder / f"brand_{i:02d}{Path(url).suffix or '.png'}"
        if dest.exists() and dest.stat().st_size > 4000:
            saved.append(dest)
            continue
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BuyOrSkip/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
        except Exception:
            continue
        if len(data) < 4000:
            continue
        dest.write_bytes(data)
        saved.append(dest)
    return saved


def ensure_public_stills(root: Path, episode: dict, chapters: list[dict]) -> list[Path]:
    del chapters
    return download_brand_stills(root, episode)
