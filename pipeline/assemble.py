from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pipeline.chapters import apply_chapter_stamps
from pipeline.detect import find_ffmpeg, media_duration_sec
from pipeline.footage import chapter_media, ensure_public_stills, footage_dir
from pipeline.slides import render_auto_beats, render_slides, render_vertical_slides


def _disclosure(root: Path) -> str:
    ch = json.loads((root / "config" / "channel.json").read_text(encoding="utf-8"))
    return str(ch.get("disclosure") or "")


def _run(ffmpeg: str, args: list[str]) -> None:
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def _ken_burns(ffmpeg: str, image: Path, seconds: float, size: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h = (int(x) for x in size.split(":"))
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,format=yuv420p"
    _run(
        ffmpeg,
        [
            "-loop",
            "1",
            "-i",
            str(image),
            "-vf",
            vf,
            "-t",
            f"{seconds:.3f}",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dest),
        ],
    )


def _fit_video(ffmpeg: str, source: Path, seconds: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "fps=30,format=yuv420p"
    )
    _run(
        ffmpeg,
        [
            "-stream_loop",
            "-1",
            "-i",
            str(source),
            "-vf",
            vf,
            "-t",
            f"{seconds:.3f}",
            "-r",
            "30",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
    )


def _concat_clips(ffmpeg: str, clips: list[Path], dest: Path) -> None:
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in clips), encoding="utf-8")
    _run(ffmpeg, ["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dest)])


def _mix(ffmpeg: str, silent: Path, voice: Path, dest: Path, *, seconds: float | None = None) -> None:
    args = ["-i", str(silent), "-i", str(voice), "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]
    if seconds is not None:
        args.extend(["-t", f"{seconds:.3f}"])
    args.extend(["-shortest", str(dest)])
    _run(ffmpeg, args)


def _slideshow(ffmpeg: str, slides: list[Path], duration: float, size: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, len(slides))
    each = max(1.8, duration / n)
    lst = dest.with_suffix(".ffconcat")
    lines = ["ffconcat version 1.0"]
    for slide in slides:
        lines.append(f"file '{slide.resolve().as_posix()}'")
        lines.append(f"duration {each:.3f}")
    lines.append(f"file '{slides[-1].resolve().as_posix()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    w, h = (int(x) for x in size.split(":"))
    _run(
        ffmpeg,
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-protocol_whitelist",
            "file,crypto,data",
            "-i",
            str(lst),
            "-vf",
            f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,format=yuv420p",
            "-t",
            f"{duration:.3f}",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dest),
        ],
    )


def _brand_still(root: Path, episode: dict) -> Path | None:
    auto = footage_dir(root, episode) / "auto"
    if not auto.is_dir():
        return None
    for path in sorted(auto.iterdir()):
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and path.stat().st_size > 4000:
            return path
    return None


def _chapter_visuals(root: Path, episode: dict, chapter: dict, out_dir: Path) -> list[Path]:
    media = chapter_media(root, episode, chapter)
    if media["videos"]:
        return media["videos"]
    beats = render_auto_beats(
        episode,
        chapter,
        out_dir / "beats" / str(chapter.get("id") or "full"),
        brand=_brand_still(root, episode),
    )
    if media["stills"]:
        return beats + media["stills"]
    return beats


def _is_video(path: Path) -> bool:
    return path.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}


def assemble_long(episode: dict, out_dir: Path, voice_path: Path, *, root: Path, chapter_audio: list[dict] | None = None) -> Path:
    ffmpeg = find_ffmpeg()
    out = out_dir / f"{episode['id']}_long.mp4"
    if chapter_audio:
        ensure_public_stills(root, episode, chapter_audio)
        work = out_dir / "_chapters"
        work.mkdir(parents=True, exist_ok=True)
        mixed: list[Path] = []
        for item in chapter_audio:
            seconds = float(item["duration"])
            visuals = _chapter_visuals(root, episode, item, out_dir)
            silent = work / f"{item['id']}_silent.mp4"
            first = visuals[0]
            if _is_video(first):
                _fit_video(ffmpeg, first, seconds, silent)
            else:
                _slideshow(ffmpeg, visuals, seconds, "1920:1080", silent)
            clip = work / f"{item['id']}.mp4"
            _mix(ffmpeg, silent, Path(item["audio"]), clip, seconds=seconds)
            mixed.append(clip)
        _concat_clips(ffmpeg, mixed, out)
        apply_chapter_stamps(episode, chapter_audio)
    else:
        seconds = max(12.0, media_duration_sec(voice_path))
        slides = render_slides(episode, out_dir)
        silent = out_dir / "_video_silent.mp4"
        _slideshow(ffmpeg, slides, seconds, "1920:1080", silent)
        _mix(ffmpeg, silent, voice_path, out)
    (out_dir / "disclosure.txt").write_text(_disclosure(root), encoding="utf-8")
    (out_dir / "description.txt").write_text(str(episode.get("description") or ""), encoding="utf-8")
    return out


def assemble_trailer(episode: dict, out_dir: Path, voice_path: Path, *, root: Path) -> Path:
    del root
    ffmpeg = find_ffmpeg()
    vslides = render_vertical_slides(episode, out_dir)
    silent = out_dir / "_short_silent.mp4"
    _slideshow(ffmpeg, vslides, 28.0, "1080:1920", silent)
    out = out_dir / f"{episode['id']}_short.mp4"
    _mix(ffmpeg, silent, voice_path, out, seconds=28.0)
    return out
