from __future__ import annotations

import asyncio
from pathlib import Path

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-2%"
PITCH = "+0Hz"


async def _save(text: str, dest: Path) -> None:
    import edge_tts

    dest.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(dest))


def generate_voiceover(episode: dict, out_dir: Path) -> Path:
    lines = episode.get("narration") or []
    if isinstance(lines, str):
        text = lines.strip()
    else:
        text = " ".join(str(x).strip() for x in lines if str(x).strip())
    if not text:
        raise ValueError("Episode has empty narration")
    dest = out_dir / "voice.mp3"
    asyncio.run(_save(text, dest))
    return dest
