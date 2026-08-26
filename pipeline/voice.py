from __future__ import annotations

import asyncio
from pathlib import Path

from pipeline.chapters import episode_chapters, short_text
from pipeline.detect import media_duration_sec

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-2%"
PITCH = "+0Hz"


async def _save(text: str, dest: Path, *, tries: int = 4) -> None:
    import edge_tts
    from edge_tts.exceptions import NoAudioReceived

    dest.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(tries):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
            await communicate.save(str(dest))
            if dest.exists() and dest.stat().st_size > 1000:
                return
            last = RuntimeError(f"TTS wrote empty file: {dest}")
        except NoAudioReceived as exc:
            last = exc
        if dest.exists():
            dest.unlink(missing_ok=True)
        await asyncio.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"TTS failed for {dest.name}: {last}")


async def _save_many(items: list[tuple[str, Path]]) -> None:
    for text, dest in items:
        print(f"TTS: {dest.stem} ({len(text.split())} words)", flush=True)
        await asyncio.wait_for(_save(text, dest), timeout=120)


def generate_voiceover(episode: dict, out_dir: Path) -> Path:
    chapters = episode_chapters(episode)
    text = " ".join(c["narration"] for c in chapters if c.get("narration"))
    if not text:
        raise ValueError("Episode has empty narration")
    dest = out_dir / "voice.mp3"
    asyncio.run(_save(text, dest))
    return dest


def generate_short_voice(episode: dict, out_dir: Path) -> Path:
    dest = out_dir / "voice_short.mp3"
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    asyncio.run(_save(short_text(episode), dest))
    return dest


def generate_chapter_audio(episode: dict, out_dir: Path) -> list[dict]:
    audio_dir = out_dir / "chapter_audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, Path, dict]] = []
    pending: list[tuple[str, Path]] = []
    for chapter in episode_chapters(episode):
        path = audio_dir / f"{chapter['id']}.mp3"
        jobs.append((chapter["narration"], path, chapter))
        if not (path.exists() and path.stat().st_size > 1000):
            pending.append((chapter["narration"], path))
    if not jobs:
        raise ValueError("Episode has empty narration")
    if pending:
        asyncio.run(_save_many(pending))
    else:
        print("Voice: reusing existing chapter audio", flush=True)
    built: list[dict] = []
    for text, path, chapter in jobs:
        del text
        built.append(
            {
                **chapter,
                "audio": path,
                "duration": max(2.4, media_duration_sec(path)),
            }
        )
    return built
