from __future__ import annotations

from pathlib import Path

CHANNEL = "Buy or Skip"
HANDLE = "@BuyOrSkip"
TAGLINE = "Adult tool reviews. One verdict."

PROGRAM_RGB = {
    "hostinger": (124, 92, 255),
    "canva": (0, 196, 204),
    "nordvpn": (74, 144, 255),
    "amazon_in": (255, 170, 51),
}

BG = (10, 12, 16)
INK = (245, 243, 238)
MUTED = (160, 164, 172)
GOLD = (232, 180, 74)


def program_color(episode: dict) -> tuple[int, int, int]:
    pid = str((episode.get("affiliate") or {}).get("program") or "")
    return PROGRAM_RGB.get(pid, GOLD)


def fonts() -> tuple[Path, Path]:
    candidates = [
        (Path(r"C:\Windows\Fonts\segoeuib.ttf"), Path(r"C:\Windows\Fonts\segoeui.ttf")),
        (Path(r"C:\Windows\Fonts\arialbd.ttf"), Path(r"C:\Windows\Fonts\arial.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")),
        (Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"), Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")),
    ]
    for bold, regular in candidates:
        if bold.exists() and regular.exists():
            return bold, regular
    raise FileNotFoundError("No usable TTF fonts (Segoe/Arial/DejaVu/Liberation)")
