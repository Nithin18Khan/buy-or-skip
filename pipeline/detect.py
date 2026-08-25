from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def which(name: str) -> str | None:
    return shutil.which(name)


def find_ffmpeg() -> str:
    exe = which("ffmpeg")
    if not exe:
        raise FileNotFoundError("ffmpeg not on PATH")
    return exe


def find_ffprobe() -> str:
    exe = which("ffprobe")
    if not exe:
        raise FileNotFoundError("ffprobe not on PATH")
    return exe


def media_duration_sec(path: Path) -> float:
    probe = find_ffprobe()
    out = subprocess.check_output(
        [
            probe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip() or "0")


def print_tool_report(root: Path) -> int:
    print("=== Money Tools factory ===")
    print(f"Root:     {root}")
    for name in ("python", "ffmpeg", "ffprobe"):
        path = which(name) if name != "python" else which("python")
        print(f"{name:10} {path or 'MISSING'}")
    ch = root / "config" / "channel.json"
    print(f"config:   {'ok' if ch.exists() else 'MISSING'}")
    print("Kids Edu Shorts credentials must never be copied here.")
    return 0 if which("ffmpeg") else 1
