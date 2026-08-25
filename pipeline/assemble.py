from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pipeline.detect import find_ffmpeg, media_duration_sec
from pipeline.slides import render_slides, render_vertical_slides


def _disclosure(root: Path) -> str:
    ch = json.loads((root / "config" / "channel.json").read_text(encoding="utf-8"))
    return str(ch.get("disclosure") or "")


def _slideshow(ffmpeg: str, slides: list[Path], duration: float, size: str, dest: Path) -> None:
    n = max(1, len(slides))
    each = max(2.2, duration / n)
    dest.parent.mkdir(parents=True, exist_ok=True)
    lst = dest.with_suffix(".txt")
    lines = []
    for p in slides:
        lines.append(f"file '{p.resolve().as_posix()}'")
        lines.append(f"duration {each:.3f}")
    lines.append(f"file '{slides[-1].resolve().as_posix()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-vf",
            f"scale={size},format=yuv420p",
            "-r",
            "30",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
    )


def assemble_long(episode: dict, out_dir: Path, voice_path: Path, *, root: Path) -> Path:
    ffmpeg = find_ffmpeg()
    seconds = max(12.0, media_duration_sec(voice_path))
    slides = render_slides(episode, out_dir)
    silent = out_dir / "_video_silent.mp4"
    _slideshow(ffmpeg, slides, seconds, "1920:1080", silent)
    out = out_dir / f"{episode['id']}_long.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(silent),
            "-i",
            str(voice_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(out),
        ],
        check=True,
        cwd=str(root),
    )
    (out_dir / "disclosure.txt").write_text(_disclosure(root), encoding="utf-8")
    return out


def assemble_trailer(episode: dict, out_dir: Path, voice_path: Path, *, root: Path) -> Path:
    ffmpeg = find_ffmpeg()
    vslides = render_vertical_slides(episode, out_dir)
    silent = out_dir / "_short_silent.mp4"
    _slideshow(ffmpeg, vslides, 28.0, "1080:1920", silent)
    out = out_dir / f"{episode['id']}_short.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(silent),
            "-i",
            str(voice_path),
            "-t",
            "28",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(out),
        ],
        check=True,
        cwd=str(root),
    )
    return out
